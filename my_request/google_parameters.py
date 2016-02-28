import datetime
import math
import time

from data import results
from my_request import my_parameters

__author__ = 'ielemin'


# An individual GoogleMapsAPI requestGroup parameters
class RequestGroupParams:
    def __init__(self, req_timestamp, var_points, base_params):
        self.req_timestamp = req_timestamp
        self.var_points = var_points
        self.base_params = base_params

    @property
    def origins(self):
        if self.base_params.is_destination_fixed:
            return self.var_points
        else:
            return [self.base_params.fixed_point]  # array of size=1

    @property
    def destinations(self):
        if self.base_params.is_destination_fixed:
            return [self.base_params.fixed_point]  # array of size=1
        else:
            return self.var_points

    def to_string(self):
        print("----- Request start -----")
        print("Request formatted on %s UTC" % datetime.datetime.utcfromtimestamp(self.req_timestamp))
        print("Arrival time: %s" % self.base_params.fixedTime)
        print("Transportation mode: %s" % self.base_params.mode)
        print("Unit system used: %s" % self.base_params.units)
        print("Origin(s): %d" % len(self.origins))
        for originIndex in range(0, len(self.origins)):
            print("* (%f deg,%f deg)" % (self.origins[originIndex][0], self.origins[originIndex][1]))
        print("Destination(s): %d" % len(self.destinations))
        for destinationIndex in range(0, len(self.destinations)):
            print(
                "* (%f deg,%f deg)" % (self.destinations[destinationIndex][0], self.destinations[destinationIndex][1]))
        print("------ Request end ------")

    def analyze_results(self, current_results):  # GoogleAPI format
        items = []
        if not results:
            return
        for oIdx in range(0, len(current_results['origin_addresses'])):
            o_geocode = current_results['origin_addresses'][oIdx]
            for dIdx in range(0, len(current_results['destination_addresses'])):
                d_geocode = current_results['destination_addresses'][dIdx]
                nfo = current_results['rows'][oIdx]['elements'][dIdx]  # info on the path result
                # TODO implement different outputs for different statuses
                # eg do not permanently discard OVER_QUERY_LIMIT results
                if nfo['status'] != u'OK':
                    items.append(results.ResultItem(self.req_timestamp, self.origins[oIdx], self.destinations[dIdx],
                                                    self.base_params.isDestinationFixed,
                                                    self.base_params.fixedTime, self.base_params.mode, o_geocode,
                                                    d_geocode,
                                                    'N/A', -1, 'N/A',
                                                    -1, ))  # Default value -> do not request it again
                else:
                    items.append(results.ResultItem(self.req_timestamp, self.origins[oIdx], self.destinations[dIdx],
                                                    self.base_params.isDestinationFixed,
                                                    self.base_params.fixedTime, self.base_params.mode, o_geocode,
                                                    d_geocode,
                                                    nfo['distance']['text'], nfo['distance']['value'],
                                                    nfo['duration']['text'], nfo['duration']['value']))
        return items  # [results.ResultItem]


# The container for all the requests
class RequestGroupContainer:
    # TODO check actual GoogleAPI value
    maxRequestSize = 49

    def __init__(self, base_params):
        self.var_points = []  # array of any size
        self.base_params = base_params

    # Instantiate with an existing instance's params
    @classmethod
    def shallow_copy(cls, rgc):  # RequestGroupContainer
        return cls(rgc.base_params)

    def append(self, var_points):
        for idx in range(0, len(var_points)):
            self.var_points.append(var_points[idx])

    # Grouping the request in buckets
    def get_request_buckets(self):
        output = []
        nb_full_requests = int(math.floor(len(self.var_points) / self.maxRequestSize))
        req_time = time.mktime(datetime.datetime.now().timetuple())
        # Full requests
        for idx in range(0, nb_full_requests):
            var_points_bucket = self.var_points[idx * self.maxRequestSize:(idx + 1) * self.maxRequestSize]
            output.append(RequestGroupParams(req_time, var_points_bucket, self.base_params))
        # Remainder
        var_points_bucket = self.var_points[nb_full_requests * self.maxRequestSize:]
        output.append(RequestGroupParams(req_time, var_points_bucket, self.base_params))

        return output

    def split(self):
        output = []
        for varPoint in self.var_points:
            output.append(my_parameters.RequestItemParams(varPoint, self.base_params))
        return output  # [my_parameters.request_item_params]

    # Not grouping the requests
    def to_string(self):
        RequestGroupParams(time.mktime(datetime.datetime.now().timetuple()), self.var_points,
                           self.base_params).to_string()

    # Grouping the request in buckets
    def to_string_buckets(self):
        requests = self.get_request_buckets()
        for requestIndex in range(0, len(requests)):
            requests[requestIndex].to_string()

    def __len__(self):
        return len(self.var_points)
