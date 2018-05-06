import os
from multiprocessing import Process, Pool, Queue
import operator
import pickle
import csv
import math
from Link import LinkData, LinkDataProcess
from Probe import ProbeData, ProbeAdditionalInfo, ProbeDataProcess

class ProbeMapMatching:
    def __init__(self, sourcepath, linkfilename, probefilename, tgtpath):
        self.sourcepath = sourcepath
        self.tgtpath = tgtpath
        self.linkfilename = linkfilename
        self.probefilename = probefilename
        self.linkfile = os.path.join(self.sourcepath, self.linkfilename)
        self.probefile = os.path.join(self.sourcepath, self.probefilename)
        self.mappedfilename = 'MatchedPoints.csv'
        self.mappedfile = os.path.join(self.tgtpath, self.mappedfilename)
        self.slopefilename = 'MatchedPointsSlope.csv'
        self.slopefile = os.path.join(self.tgtpath, self.slopefilename)

    def loadData(self):
        self.geohashmap7prec, self.geohashmap8prec, self.linkInfo = LinkDataProcess(self.sourcepath, self.linkfilename, self.tgtpath).loadData()
        self.probeInfo, self.addiInfo = ProbeDataProcess(self.sourcepath, self.probefilename, self.tgtpath, self.geohashmap7prec, self.geohashmap8prec).loadData()     

    def run(self):
        print('\n\nProcess probe data mapping now...')
        with Pool() as pool:
            result = pool.map(self.probeMatching, self.probeInfo)
            pool.close()
            pool.join()
            print('\n\nFinish probe data mapping!')
            resultfile = os.path.join(self.tgtpath, 'result.pickle')
            self.dumpFilewithPickle(resultfile, result)
            print('\n\nSave result to files now...')

            with open(self.mappedfile, 'w') as mapfile, open(self.slopefile, 'w') as slopefile:
                mapfilewriter = csv.writer(mapfile, delimiter = ',')
                slopefilewriter = csv.writer(slopefile, delimiter = ',')
                title = ['sampleID', 'dateTime', 'sourceCode', 'latitude', 'longitude', 'altitude', 'speed', 'heading', 'linkPVID', 'direction', 'distFromRef', 'distFromLink']
                mapfilewriter.writerow(title)
                title = ['sampleID', 'dateTime', 'latitude', 'longitude', 'altitude', 'probeSlope', 'linkSlope']
                slopefilewriter.writerow(title)
                accerror, probenum, totalnum = 0.0, 0, 0
                for idx, probepoint in enumerate(result):
                    if not probepoint.mappingsucessful:
                        continue
                    if len(self.addiInfo[idx].dateTimelist) == len(self.addiInfo[idx].sourceCodelist) \
                        == len(self.addiInfo[idx].speedlist) == len(self.addiInfo[idx].headinglist) \
                        == len(probepoint.shapeInfo) == len(probepoint.distFromRef) == len(probepoint.distFromLink):
                        i = 0
                        while i < len(self.addiInfo[idx].dateTimelist):
                            line = [probepoint.sampleID, self.addiInfo[idx].dateTimelist[i], self.addiInfo[idx].sourceCodelist[i], \
                                    probepoint.shapeInfo[i][0], probepoint.shapeInfo[i][1], probepoint.shapeInfo[i][2] if len(probepoint.shapeInfo[i]) == 3 else '', self.addiInfo[idx].speedlist[i], self.addiInfo[idx].headinglist[i], \
                                    probepoint.maplinkID, probepoint.distFromRef[i], probepoint.distFromLink[i]]
                            mapfilewriter.writerow(line)

                            line = [probepoint.sampleID, self.addiInfo[idx].dateTimelist[i], probepoint.shapeInfo[i][0], probepoint.shapeInfo[i][1], probepoint.shapeInfo[i][2] if len(probepoint.shapeInfo[i]) == 3 else '', probepoint.slpoe[i], self.linkInfo[probepoint.maplinkID].avgslope if self.linkInfo[probepoint.maplinkID].avgslope != None else '']
                            slopefilewriter.writerow(line)

                            if line[-1] != '' and line[-1] < 5.0:
                                accerror += ((line[-1] - line[-2])**2)
                                probenum += 1

                            i += 1
                            totalnum += 1
                    else:
                        print("ERROR: Number of records is invalid, for probe data: ", probepoint.sampleID)
            print("\nTotally {} probe points are compared with link probe".format(probenum))
            print('accuaracy mean square error is: {}'.format(accerror / probenum))
            print('mean square error is: {}'.format(accerror / totalnum))
            print('Root mean square error is: {}'.format(math.sqrt(accerror/totalnum)))
            
    def probeMatching(self, probePoint):
        distancelist = [self.linkInfo[candidate].calcavgdistance(probePoint.shapeInfo) for candidate in probePoint.candidatelist]
        idx, mindist = min(enumerate(distancelist), key=operator.itemgetter(1))
        linkid = probePoint.candidatelist[idx]
        distfromreflist = self.linkInfo[linkid].calcdistanceFromRef(probePoint.shapeInfo)
        distfromlinklist = self.linkInfo[linkid].calcdistanceFromLink(probePoint.shapeInfo)
        probePoint.setMapInfo(linkid, distfromreflist, distfromlinklist)
        probePoint.setSlope(self.linkInfo[linkid].refInfo)
        return probePoint

    def loadFilewithPickle(self, file):
        with open(file, 'rb') as loadfile:
            return pickle.load(loadfile)

    def dumpFilewithPickle(self, file, content):
        with open(file, 'wb') as savefile:
            pickle.dump(content, savefile)

def main():
    sourcepath, tgtpath = '../probe_data_map_matching', '../probe_data_map_matching'
    linkdatafilename, probedatafilename = 'Partition6467LinkData.csv', 'Partition6467ProbePoints.csv'
    matchProcess = ProbeMapMatching(sourcepath, linkdatafilename, probedatafilename, tgtpath)
    matchProcess.loadData()
    matchProcess.run()
    
if __name__ == '__main__':
    main()