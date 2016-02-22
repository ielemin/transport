__author__ = 'adrien'

import sys
import googlemaps
import googlemaps.client


class GoogleAPI:
    def __init__(self, keyFileName):
        keyFile = open(keyFileName, 'r')
        self.key = keyFile.read()
        self.origins = []
        try:
            # See client.py for other optional __init__ parameters
            self.client = googlemaps.Client(key=self.key, retry_timeout=10)
        except ValueError as e:
            print("#####")
            print("Exception in instantiating GoogleAPI service: %s" % e.message)
            print("Exception args: %s" % e.args)
            print("#####")
            raise
        except:
            print("#####")
            print("Unknown exception at GoogleAPI instantiation")
            print("#####")
            raise

    def SetOrigins(self, origins):
        self.origins = origins

    def GetLatLng(self, location):
        output = None
        try:
            geocode_obj = self.client.geocode(location)
        except googlemaps.exceptions.ApiError as e:
            print("#####")
            print("Exception in GoogleAPI request ('ApiError'): %s" % e.message)
            print("Exception status: %s" % e.status)
            for arg in e.args:
                print("Exception args: %s" % arg)
            print("#####")
            output = None
            raise e
        except googlemaps.exceptions.HTTPError as e:
            print("#####")
            print("Exception in GoogleAPI request ('HTTPError'): %s" % e.message)
            print("Exception base exception: %s" % e.base_exception)
            print("Exception status: %s" % e.status_code)
            for arg in e.args:
                print("Exception args: %s" % arg)
            print("#####")
            output = None
            raise e
        except googlemaps.exceptions.Timeout as e:
            print("#####")
            print("Exception in GoogleAPI request ('Timeout'): %s" % e.message)
            for arg in e.args:
                print("Exception args: %s" % arg)
            print("#####")
            output = None
            raise e
        except googlemaps.exceptions.TransportError as e:
            print("#####")
            print("Exception in GoogleAPI request ('TransportError'): %s" % e.message)
            print("Exception base exception: %s" % e.base_exception)
            for arg in e.args:
                print("Exception args: %s" % arg)
            print("#####")
            output = None
            raise e
        except:
            print("#####")
            print("Unexpected error:", sys.exc_info()[0])
            print("#####")
            output = None
            raise
        else:
            location = geocode_obj[0]['geometry']['location']
            output = [location['lat'], location['lng']]
            return output

    def GetClient(self):
        return self.client

    def GetDistances(self, requestParams):  # RequestGroupParams
        origins = requestParams.origins
        if len(origins) == 0: return
        destinations = requestParams.destinations
        self.SetOrigins(origins)
        try:
            if requestParams.baseParams.isDestinationFixed:
                output = self.client.distance_matrix(origins=self.origins, destinations=destinations,
                                                     mode=requestParams.baseParams.mode,
                                                     units=requestParams.baseParams.units,
                                                     arrival_time=requestParams.baseParams.fixedTime)
            else:
                output = self.client.distance_matrix(origins=self.origins, destinations=destinations,
                                                     mode=requestParams.baseParams.mode,
                                                     units=requestParams.baseParams.units,
                                                     departure_time=requestParams.baseParams.fixedTime)
        except googlemaps.exceptions.ApiError as e:
            print("#####")
            print("Exception in GoogleAPI request ('ApiError'): %s" % e.message)
            print("Exception status: %s" % e.status)
            for arg in e.args:
                print("Exception args: %s" % arg)
            print("#####")
            raise e
        except googlemaps.exceptions.HTTPError as e:
            print("#####")
            print("Exception in GoogleAPI request ('HTTPError'): %s" % e.message)
            print("Exception base exception: %s" % e.base_exception)
            print("Exception status: %s" % e.status_code)
            for arg in e.args:
                print("Exception args: %s" % arg)
            print("#####")
            raise e
        except googlemaps.exceptions.Timeout as e:
            print("#####")
            print("Exception in GoogleAPI request ('Timeout'): %s" % e.message)
            for arg in e.args:
                print("Exception args: %s" % arg)
            print("#####")
            raise e
        except googlemaps.exceptions.TransportError as e:
            print("#####")
            print("Exception in GoogleAPI request ('TransportError'): %s" % e.message)
            print("Exception base exception: %s" % e.base_exception)
            for arg in e.args:
                print("Exception args: %s" % arg)
            print("#####")
            raise e
        except:
            print("#####")
            print("Unexpected error:", sys.exc_info()[0])
            print("#####")
            raise
        else:
            return output

    # TODO properly catch exceptions raised by GetDistances()
    def DoRequest(self, requestContainer):
        # Request the results and Append them in the same object
        output = []
        requests = requestContainer.GetRequestBuckets()
        for requestIndex in range(0, len(requests)):
            currentRequest = requests[requestIndex]  # RequestGroupParams
            currentResults = self.GetDistances(currentRequest)  # GoogleAPI format
            if not (currentResults): continue
            currentFormattedResults = currentRequest.analyzeResults(currentResults)  # [ResultItem]
            output.extend(currentFormattedResults)
        return output  # [ResultItem]
