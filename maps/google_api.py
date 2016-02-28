import sys
import googlemaps
import googlemaps.client

__author__ = 'ielemin'


class GoogleAPI:
    def __init__(self, key_filename):
        key_file = open(key_filename, 'r')
        self.key = key_file.read()
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

    def set_origins(self, origins):
        self.origins = origins

    def get_latlng(self, location):
        try:
            geocode_obj = self.client.geocode(location)
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
            location = geocode_obj[0]['geometry']['location']
            output = [location['lat'], location['lng']]
            return output

    def get_client(self):
        return self.client

    def get_distances(self, request_params):  # RequestGroupParams
        origins = request_params.origins
        if len(origins) == 0:
            return
        destinations = request_params.destinations
        self.set_origins(origins)
        try:
            if request_params.baseParams.isDestinationFixed:
                output = self.client.distance_matrix(origins=self.origins, destinations=destinations,
                                                     mode=request_params.baseParams.mode,
                                                     units=request_params.baseParams.units,
                                                     arrival_time=request_params.baseParams.fixedTime)
            else:
                output = self.client.distance_matrix(origins=self.origins, destinations=destinations,
                                                     mode=request_params.baseParams.mode,
                                                     units=request_params.baseParams.units,
                                                     departure_time=request_params.baseParams.fixedTime)
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

    # TODO properly catch exceptions raised by get_distances()
    def do_request(self, request_container):
        # Request the results and append them in the same object
        output = []
        requests = request_container.get_request_buckets()
        for request_idx in range(0, len(requests)):
            current_request = requests[request_idx]  # RequestGroupParams
            current_results = self.get_distances(current_request)  # GoogleAPI format
            if not current_results:
                continue
            current_formatted_results = current_request.analyze_results(current_results)  # [ResultItem]
            output.extend(current_formatted_results)
        return output  # [ResultItem]
