__author__ = 'adrien'

import webbrowser
from os import path
from pyhull.voronoi import VoronoiTess
from matplotlib.path import Path
import numpy as np
from maps import js_map_generator
from data import serialization
from my_request import google_parameters
from util import my_io
from maps import mapgrid
from maps import geocode

abspath = my_io.myIO.abspath


class Display:
    def __init__(self, service, doDeserialization, doRequest, strictMatch, useGeocodeAddress, zoomLevel):
        self.service = service
        self.doDeserialization = doDeserialization
        self.doRequest = doRequest
        self.strictMatch = strictMatch
        self.allResultsList = serialization.ResultList()  # The UNIQUE ResultList
        self.GeocodeList = geocode.GeocodeList(service)  # The UNIQUE geocode.GeocodeList
        self.resultsDir = abspath + "/results"
        self.geocodeDir = abspath + "/geocode"
        self.outDir = abspath + "/out"
        self.useGeocodeAddress = useGeocodeAddress
        self.zoomLevel = zoomLevel
        return

    def LoadExistingResults(self):
        # Load the serialized results
        if not (self.doDeserialization):
            return

        inputName = my_io.myIO.GetMostRecentFromTemplate(self.resultsDir, "result")  # Where the ResultList was stored
        self.allResultsList.importItems(serialization.ResultList.Deserialize(inputName))

    def LoadExistingGeocodes(self):
        # Load the serialized geocodes
        if not (self.doDeserialization):
            return

        inputName = my_io.myIO.GetMostRecentFromTemplate(self.geocodeDir, "geocode")  # Where the geocode.GeocodeList was stored
        self.GeocodeList.importItems(geocode.GeocodeList.Deserialize(inputName), isForce=False)

    def FilterExistingResults(self, mapGridInstance):  # mapGridInstance = instance of the request
        myResultsToDisplay = []  # [ResultItem]
        if self.strictMatch:
            for req in mapGridInstance.GenerateRequests().Split():
                res = self.allResultsList.GetByRequest(req)
                if res:
                    myResultsToDisplay.append(res)
        else:
            for res in self.allResultsList.items:
                if mapGridInstance.IsMatch(res.RequestItemParams, self.strictMatch):
                    myResultsToDisplay.append(res)

        return myResultsToDisplay  # [ResultItem]

    def substituteGeocodeLatLng(self, resultItems):  # [ResultItem]
        # TODO WOW WOW WOW it seems to change the originLatLng in the serialized list !!
        return resultItems
        print("----- Geocode substitution start -----")
        if not self.useGeocodeAddress:
            print("Substitution disabled: nothing to do")
            print("------ Geocode substitution end ------")
            return resultItems
        oToUdate = set()  # [ResultItem]
        dToUdate = set()  # [ResultItem]
        # First, get all the already existing geocode equivalents
        oSubs1Count = 0
        dSubs1Count = 0
        for item in resultItems:
            oGeocodeLatLng = self.GeocodeList.GetByKey(item.originGeocode)
            if oGeocodeLatLng != None:
                # print("Substituting in origin '%s' the grid coordinates %s by the actual coordinates %s" % (
                # item.originGeocode, item.originLatLng, oGeocodeLatLng))
                item.originLatLng = oGeocodeLatLng
                oSubs1Count += 1
            else:
                oToUdate.add(item)
            dGeocodeLatLng = self.GeocodeList.GetByKey(item.destinationGeocode)
            if dGeocodeLatLng != None:
                # print("Substituting in destination '%s' the grid coordinates %s by the actual coordinates %s" % (
                # item.destinationGeocode, item.destinationLatLng, dGeocodeLatLng))
                item.destinationLatLng = dGeocodeLatLng
                dSubs1Count += 1
            else:
                dToUdate.add(item)
        print("There are %d origin(s) and %d destination(s) with a geocoding substitution" % (oSubs1Count, dSubs1Count))
        print("There are %d origin(s) and %d destination(s) with no geocoding values" % (len(oToUdate), len(dToUdate)))
        print("Performing requests...")
        # Then for the missing ones, try to get them. If an exception is raised, stop asking the GoogleAPI service
        oReqCount = 0
        dReqCount = 0
        oSubs2Count = 0
        dSubs2Count = 0
        try:
            for oItem in oToUdate:
                oGeocodeLatLng = self.GeocodeList.RequestAndAdd(oItem.originGeocode)
                if oGeocodeLatLng != None:
                    # print("Substituting in origin '%s' the grid coordinates %s by the actual coordinates %s" % (
                    # oItem.originGeocode, oItem.originLatLng, oGeocodeLatLng))
                    oItem.originLatLng = oGeocodeLatLng
                    oSubs2Count += 1
                oReqCount += 1
            for dItem in dToUdate:
                dGeocodeLatLng = self.GeocodeList.RequestAndAdd(dItem.destinationGeocode)
                if dGeocodeLatLng != None:
                    # print("Substituting in destination '%s' the grid coordinates %s by the actual coordinates %s" % (
                    # dItem.destinationGeocode, dItem.destinationLatLng, dGeocodeLatLng))
                    dItem.destinationLatLng = dGeocodeLatLng
                    dSubs2Count += 1
                dReqCount += 1
        except:
            print("Caught API exception. stopping requests")
        finally:
            print("Missing origins: %s | Requested: %d | Substituted: %d" % (len(oToUdate), oReqCount, oSubs2Count))
            print(
                "Missing destinations: %s | Requested: %d | Substituted: %d" % (len(dToUdate), dReqCount, dSubs2Count))
            print("------ Geocode substitution end ------")
            return resultItems

    def GetDataToDisplay(self, mapGridInstance):
        strictRequestContainer = mapGridInstance.GenerateRequests()

        # Load the serialized results
        self.LoadExistingResults()

        # Load the serialized geocodes
        self.LoadExistingGeocodes()

        # Filter the serialized results that already match the request base params
        myResultsToDisplay = self.FilterExistingResults(mapGridInstance)  # [ResultItem]
        print('Found %d requests already saved' % len(myResultsToDisplay))

        print("----- Request matching start -----")
        # TODO Lookup for a more efficient algorithm, esp for long lists
        myRequestContainer = google_parameters.RequestGroupContainer.ShallowCopy(strictRequestContainer)  # RequestGroupContainer
        print("Matching %d requests with %d results" % (len(strictRequestContainer), len(myResultsToDisplay)))
        nbReqFound = 0
        for req in strictRequestContainer.Split():  # RequestItemParams
            isReqFound = False
            for res in myResultsToDisplay:
                if req.IsMatch(res.RequestItemParams):
                    isReqFound = True
                    nbReqFound += 1
                    break
            if not isReqFound:
                myRequestContainer.Append([req.varPoint])
        print("Found %d/%d matching results" % (nbReqFound, len(strictRequestContainer)))
        print("------ Request matching end ------")

        print("----- GoogleAPI request start -----")
        # TODO properly catch exceptions raised by DoRequest()
        requestResultItems = []
        if self.doRequest:
            print("There are %d atomic requests to perform" % len(myRequestContainer))
            requestResultItems.extend(self.service.DoRequest(myRequestContainer))  # [ResultItem]
            print("Found %d/%d results" % (len(requestResultItems), len(myRequestContainer)))
            self.allResultsList.importItems(requestResultItems)
            myResultsToDisplay.extend(requestResultItems)
        else:
            print("Request mode is deactivated: none of the %d requests will be performed" % len(myRequestContainer))
        print("------ GoogleAPI request end ------")

        # Set properly the colors
        serialization.ResultList.SetColors(myResultsToDisplay, 8)

        myResultsToDisplay = self.substituteGeocodeLatLng(myResultsToDisplay)

        outputResultName = self.allResultsList.Serialize(self.resultsDir, "result", ".csv")
        outputGeocodeName = self.GeocodeList.Serialize(self.geocodeDir, "geocode", ".csv")

        return (strictRequestContainer.baseParams.fixedPoint, myResultsToDisplay)  # ([Lat,Lng],[ResultItem])

    def markersGMaps(self, mapGridInstance):
        (center, myResultsToDisplay) = self.GetDataToDisplay(mapGridInstance)
        if not myResultsToDisplay:
            print("Nothing to display")
            return

        # Try to use only the GetDataToDisplay output from here...
        print("----- Map build start ----")
        map = js_map_generator.JSMap(mapGridInstance.requestBaseParams.fixedPoint[0], mapGridInstance.requestBaseParams.fixedPoint[1],
                    self.zoomLevel)
        print("Writing %d results markers" % (len(myResultsToDisplay)))
        map.displayResultItems(myResultsToDisplay)
        mapName = my_io.myIO.GetUniqueName(self.outDir, "map", ".html")
        map.draw(mapName)
        print("Map file generated at %s" % mapName)
        print("Browser will try to open: 'file://%s'" % path.abspath(mapName))
        webbrowser.open_new_tab("file://" + path.abspath(mapName))
        print("------ Map build end -----")

        # Display.voronoiStandalone(myResultsToDisplay, 0.05)

    def regionsGMaps(self, mapGridInstance, tolerance):
        (center, myResultsToDisplay) = self.GetDataToDisplay(mapGridInstance)
        if not myResultsToDisplay:
            print("Nothing to display")
            return

        (minc, maxc, vRegions) = DisplayUtils.GetVoronoiRegions(myResultsToDisplay, tolerance)
        if not vRegions:
            print("No data to display")
            print("------ Diplay end ------")
            return

        # Try to use only the GetDataToDisplay output from here...
        print("----- Map build start ----")
        map = js_map_generator.JSMap(mapGridInstance.requestBaseParams.fixedPoint[0], mapGridInstance.requestBaseParams.fixedPoint[1],
                    self.zoomLevel)
        map.displayResultRegions(vRegions)
        mapName = my_io.myIO.GetUniqueName(self.outDir, "map", ".html")
        map.draw(mapName)
        print("Map file generated at %s" % mapName)
        print("Browser will try to open: 'file://%s'" % path.abspath(mapName))
        webbrowser.open_new_tab("file://" + path.abspath(mapName))
        print("------ Map build end -----")


class DisplayUtils:
    def __init__(self):
        return

    @staticmethod
    def GetVoronoiRegions(fullResults, tolerance):  # [ResultItem],float
        output = []
        markersLatLng = []  # [[Lat,Lng]]
        print("----- Voronoi start -----")
        for result in fullResults:
            markersLatLng.append(result.varPoint)
        print("Markers found: %d" % len(markersLatLng))
        print("Computing Voronoi regions")
        voronoiData = VoronoiTess(markersLatLng)
        maxc = np.amax(voronoiData.points, 0)  # [Lat,Lng]
        minc = np.amin(voronoiData.points, 0)  # [Lat,Lng]
        excludedCount = 0
        for vIdx in range(0, len(voronoiData.vertices)):
            vertex = voronoiData.vertices[vIdx]
            if not (DisplayUtils.CheckPointInCircle(vertex, minc, maxc, tolerance)):
                excludedCount += 1
                # print("Excluded vertex #%d: %s" % (vIdx, vertex))
        if (len(fullResults) != len(voronoiData.points)):
            print("Major error - #Markers: %d | #VoronoiPoints: %d" % (len(fullResults), len(voronoiData.points)))
            print("------ Voronoi end ------")
            return
        print("Total vertices excluded in the process: %d" % excludedCount)
        print("Converting Voronoi polygons in actual coordinates")
        # Convert region vertex numbers into actual coordinates
        for regionIdx in range(0, len(voronoiData.regions)):
            region = voronoiData.regions[regionIdx]
            regionCenter = voronoiData.points[regionIdx]
            coordsLatLng = []  # [[Lat,Lng]]
            for idx in region:
                if not (DisplayUtils.CheckPointInCircle(voronoiData.vertices[idx], minc, maxc, tolerance)):
                    continue  # either we break (discard region) or continue (discard only one vertex)
                coordsLatLng.append(voronoiData.vertices[idx])
            if not (coordsLatLng):
                # print("Empty vertex set for index %d" % regionIdx)
                continue
            # WARN By chance, the voronoiData.points[regionIdx] (the one at the 'center' of the region voronoiData.regions[regionIdx])
            # seems to be the same that fullResults[regionIdx] -> makes it extremely useful to retrieve the color property
            if fullResults[regionIdx].varPoint != regionCenter:
                print("Major error at index %d: marker %s does not match Voronoi point %s" % (
                    regionIdx, fullResults[regionIdx].varPoint, regionCenter))
                print("------ Voronoi end ------")
                return
            # Remove items with default constructor values
            if fullResults[regionIdx].durationValue < 0:
                continue
            output.append([coordsLatLng, fullResults[regionIdx]])  # [[[lat,lng]],resultIem]
        print("------ Voronoi end ------")
        return (minc, maxc, output)

    @staticmethod
    def GetPathFromVertices(vertices):  # [[x,y]]
        if not (vertices):
            return
        vertices.append(vertices[0])  # Add the first point at the end to close the path (actual value not used)
        codes = [Path.MOVETO]  # First, move the pen to the first point
        for i in range(0, len(vertices) - 2):
            codes.append(Path.LINETO)  # Than, draw a line with the next point
        codes.append(Path.CLOSEPOLY)  # Finally, close the path
        return Path(vertices, codes, closed=True)

    @staticmethod
    def CheckPointInSquare(point, mins, maxs, tolerance):  # [lat,lng] for 3 first params, float for the 4th
        dLat = (maxs[0] - mins[0]) / 2
        dLng = (maxs[1] - mins[1]) / 2
        minLat = mins[0] - tolerance * dLat
        maxLat = maxs[0] + tolerance * dLat
        minLng = mins[1] - tolerance * dLng  # Beware : in theory, there should be a correction to tolerance = f(Lat)
        maxLng = maxs[1] + tolerance * dLng  # Beware : in theory, there should be a correction to tolerance = f(Lat)
        if point[0] < minLat:
            return False
        elif point[0] > maxLat:
            return False
        elif point[1] < minLng:
            return False
        elif point[1] > maxLng:
            return False
        else:
            return True

    @staticmethod
    def CheckPointInCircle(point, mins, maxs, tolerance):  # [lat,lng] for 3 first params, float for the 4th
        dLat = (maxs[0] - mins[0]) / 2
        dLng = (maxs[1] - mins[1]) / 2
        cLat = (maxs[0] + mins[0]) / 2
        cLng = (maxs[1] + mins[1]) / 2
        rLat = mapgrid.MapGridUtils.GetDistance(cLat, cLng, cLat + dLat, cLng, False)
        rLng = mapgrid.MapGridUtils.GetDistance(cLat, cLng, cLat, cLng + dLng, False)
        rMax = max(rLat, rLng)
        r = mapgrid.MapGridUtils.GetDistance(cLat, cLng, point[0], point[1], False)
        return r < rMax * (1 + tolerance)

    @staticmethod
    def TestDistanceCompute():
        # Load the serialized results
        allResultsList = serialization.ResultList()  # The UNIQUE ResultList
        inputName = my_io.myIO.GetMostRecentFromTemplate(abspath + "/results", "result")  # Where the ResultList was stored
        allResultsList.importItems(serialization.ResultList.Deserialize(inputName))

        for result in allResultsList.items:
            dSimple = mapgrid.MapGridUtils.GetDistance(result.originLatLng[0], result.originLatLng[1],
                                               result.destinationLatLng[0], result.destinationLatLng[1], True)
            dExact = mapgrid.MapGridUtils.GetDistance(result.originLatLng[0], result.originLatLng[1],
                                              result.destinationLatLng[0], result.destinationLatLng[1], False)
            dGoogle = result.distanceValue / 1000.0
            print("Simple = %f | Exact = %f | Google (%s) = %f" % (dSimple, dExact, result.mode, dGoogle))
