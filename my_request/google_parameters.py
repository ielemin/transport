__author__ = 'adrien'

import datetime
import math
import time

from data import results
from my_request import my_parameters

# An individual GoogleMapsAPI requestGroup parameters
class RequestGroupParams:
    def __init__(self, reqTimestamp, varPointsArray, baseParams):
        self.reqTimestamp = reqTimestamp
        self.varPointsArray = varPointsArray
        self.baseParams = baseParams

    @property
    def origins(self):
        if self.baseParams.isDestinationFixed:
            return self.varPointsArray
        else:
            return [self.baseParams.fixedPoint]  # array of size=1

    @property
    def destinations(self):
        if self.baseParams.isDestinationFixed:
            return [self.baseParams.fixedPoint]  # array of size=1
        else:
            return self.varPointsArray

    def toString(self):
        print( "----- Request start -----")
        print( "Request formatted on %s UTC" % datetime.datetime.utcfromtimestamp(self.reqTimestamp))
        print( "Arrival time: %s" % self.baseParams.fixedTime)
        print( "Transportation mode: %s" % self.baseParams.mode)
        print( "Unit system used: %s" % self.baseParams.units)
        print( "Origin(s): %d" % len(self.origins))
        for originIndex in range(0, len(self.origins)):
            print( "* (%f deg,%f deg)" % (self.origins[originIndex][0], self.origins[originIndex][1]))
        print( "Destination(s): %d" % len(self.destinations))
        for destinationIndex in range(0, len(self.destinations)):
            print( "* (%f deg,%f deg)" % (self.destinations[destinationIndex][0], self.destinations[destinationIndex][1]))
        print( "------ Request end ------")

    def analyzeResults(self, current_results):  # GoogleAPI format
        items = []
        if not (results): return
        for oIdx in range(0, len(current_results['origin_addresses'])):
            oGeocode = current_results['origin_addresses'][oIdx]
            for dIdx in range(0, len(current_results['destination_addresses'])):
                dGeocode = current_results['destination_addresses'][dIdx]
                nfo = current_results['rows'][oIdx]['elements'][dIdx]  # info on the path result
                # TODO implement different outputs for different statuses (eg do not permanently discard OVER_QUERY_LIMIT results)
                if nfo['status'] != u'OK':
                    items.append(results.ResultItem(self.reqTimestamp, self.origins[oIdx], self.destinations[dIdx],
                                            self.baseParams.isDestinationFixed,
                                            self.baseParams.fixedTime, self.baseParams.mode, oGeocode, dGeocode,
                                            'N/A', -1, 'N/A',
                                            -1, ))  # Default value -> do not request it again
                else:
                    items.append(results.ResultItem(self.reqTimestamp, self.origins[oIdx], self.destinations[dIdx],
                                            self.baseParams.isDestinationFixed,
                                            self.baseParams.fixedTime, self.baseParams.mode, oGeocode, dGeocode,
                                            nfo['distance']['text'], nfo['distance']['value'],
                                            nfo['duration']['text'], nfo['duration']['value']))
        return items  # [results.ResultItem]


# The container for all the requests
class RequestGroupContainer:
    # TODO check actual GoogleAPI value
    maxRequestSize = 49

    def __init__(self, baseParams):
        self.varPointsArray = []  # array of any size
        self.baseParams = baseParams

    # Instantiate with an existing instance's params
    @classmethod
    def ShallowCopy(cls, rgc):  # RequestGroupContainer
        return cls(rgc.baseParams)

    def Append(self, varPoints):
        for idx in range(0, len(varPoints)):
            self.varPointsArray.append(varPoints[idx])

    # Grouping the request in buckets
    def GetRequestBuckets(self):
        output = []
        nbFullRequests = int(math.floor(len(self.varPointsArray) / self.maxRequestSize))
        reqTime = time.mktime(datetime.datetime.now().timetuple())
        # Full requests
        for idx in range(0, nbFullRequests):
            varPointsBucket = self.varPointsArray[idx * self.maxRequestSize:(idx + 1) * self.maxRequestSize]
            output.append(RequestGroupParams(reqTime, varPointsBucket, self.baseParams))
        # Remainder
        varPointsBucket = self.varPointsArray[nbFullRequests * self.maxRequestSize:]
        output.append(RequestGroupParams(reqTime, varPointsBucket, self.baseParams))

        return output

    def Split(self):
        output = []
        for varPoint in self.varPointsArray:
            output.append(my_parameters.RequestItemParams(varPoint, self.baseParams))
        return output  # [my_parameters.RequestItemParams]

    # Not grouping the requests
    def toString(self):
        RequestGroupParams(time.mktime(datetime.datetime.now().timetuple()), self.varPointsArray, self.baseParams).toString()

    # Grouping the request in buckets
    def toStringBuckets(self):
        requests = self.GetRequestBuckets()
        for requestIndex in range(0, len(requests)):
            requests[requestIndex].toString()

    def __len__(self):
        return len(self.varPointsArray)


