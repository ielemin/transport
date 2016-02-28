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

__author__ = 'ielemin'

abspath = my_io.MyIO.abspath


class Display:
    def __init__(self, service, do_serialization, do_request, strict_match, use_geocode_address, zoom_level):
        self.service = service
        self.do_serialization = do_serialization
        self.do_request = do_request
        self.strict_match = strict_match
        self.all_results_list = serialization.ResultList()  # The UNIQUE ResultList
        self.geocode_list = geocode.GeocodeList(service)  # The UNIQUE geocode.geocode_list
        self.results_dir = abspath + "/results"
        self.geocode_dir = abspath + "/geocode"
        self.out_dir = abspath + "/out"
        self.use_geocode_address = use_geocode_address
        self.zoom_level = zoom_level
        return

    def load_existing_results(self):
        # Load the serialized results
        if not self.do_serialization:
            return

        input_name = my_io.MyIO.get_most_recent_from_template(self.results_dir, "result")  # Where the ResultList was stored
        self.all_results_list.import_items(serialization.ResultList.deserialize(input_name))

    def load_existing_geocodes(self):
        # Load the serialized geocodes
        if not self.do_serialization:
            return

        input_name = my_io.MyIO.get_most_recent_from_template(self.geocode_dir, "geocode")
        # Where the geocode.geocode_list was stored
        self.geocode_list.import_items(geocode.GeocodeList.deserialize(input_name), is_force=False)

    def filter_existing_results(self, mapgrid_instance):  # mapgrid_instance = instance of the request
        my_results_to_display = []  # [ResultItem]
        if self.strict_match:
            for req in mapgrid_instance.generate_requests().split():
                res = self.all_results_list.get_by_request(req)
                if res:
                    my_results_to_display.append(res)
        else:
            for res in self.all_results_list.items:
                if mapgrid_instance.is_match(res.request_item_params, self.strict_match):
                    my_results_to_display.append(res)

        return my_results_to_display  # [ResultItem]

    def substitute_geocode_latlng(self, results_items):  # [ResultItem]
        # TODO WOW WOW WOW it seems to change the origin_latlng in the serialized list !!
        return results_items
        print("----- Geocode substitution start -----")
        if not self.useGeocodeAddress:
            print("Substitution disabled: nothing to do")
            print("------ Geocode substitution end ------")
            return results_items
        o_to_u_date = set()  # [ResultItem]
        d_to_u_date = set()  # [ResultItem]
        # First, get all the already existing geocode equivalents
        o_subs_1_count = 0
        d_subs_1_count = 0
        for item in results_items:
            o_geocode_latlng = self.GeocodeList.get_by_key(item.originGeocode)
            if o_geocode_latlng is not None:
                # print("Substituting in origin '%s' the grid coordinates %s by the actual coordinates %s" % (
                # item.origin_geocode, item.origin_latlng, o_geocode_latlng))
                item.originLatLng = o_geocode_latlng
                o_subs_1_count += 1
            else:
                o_to_u_date.add(item)
            d_geocode_latlng = self.GeocodeList.get_by_key(item.destinationGeocode)
            if d_geocode_latlng is not None:
                # print("Substituting in destination '%s' the grid coordinates %s by the actual coordinates %s" % (
                # item.destination_geocode, item.destination_latlng, d_geocode_latlng))
                item.destinationLatLng = d_geocode_latlng
                d_subs_1_count += 1
            else:
                d_to_u_date.add(item)
        print("There are %d origin(s) and %d destination(s) with a geocoding substitution" % (
            o_subs_1_count, d_subs_1_count))
        print("There are %d origin(s) and %d destination(s) with no geocoding values" % (
            len(o_to_u_date), len(d_to_u_date)))
        print("Performing requests...")
        # Then for the missing ones, try to get them. If an exception is raised, stop asking the GoogleAPI service
        o_req_count = 0
        d_req_count = 0
        o_subs_2_count = 0
        d_subs_2_count = 0
        try:
            for oItem in o_to_u_date:
                o_geocode_latlng = self.GeocodeList.request_and_add(oItem.originGeocode)
                if o_geocode_latlng is not None:
                    # print("Substituting in origin '%s' the grid coordinates %s by the actual coordinates %s" % (
                    # oItem.origin_geocode, oItem.origin_latlng, o_geocode_latlng))
                    oItem.originLatLng = o_geocode_latlng
                    o_subs_2_count += 1
                o_req_count += 1
            for dItem in d_to_u_date:
                d_geocode_latlng = self.GeocodeList.request_and_add(dItem.destinationGeocode)
                if d_geocode_latlng is not None:
                    # print("Substituting in destination '%s' the grid coordinates %s by the actual coordinates %s" % (
                    # dItem.destination_geocode, dItem.destination_latlng, d_geocode_latlng))
                    dItem.destinationLatLng = d_geocode_latlng
                    d_subs_2_count += 1
                d_req_count += 1
        except:
            print("Caught API exception. stopping requests")
        finally:
            print("Missing origins: %s | Requested: %d | Substituted: %d" % (
                len(o_to_u_date), o_req_count, o_subs_2_count))
            print(
                "Missing destinations: %s | Requested: %d | Substituted: %d" % (
                    len(d_to_u_date), d_req_count, d_subs_2_count))
            print("------ Geocode substitution end ------")
            return results_items

    def get_data_to_display(self, mapgrid_instance):
        strictrequest_container = mapgrid_instance.generate_requests()

        # Load the serialized results
        self.load_existing_results()

        # Load the serialized geocodes
        self.load_existing_geocodes()

        # Filter the serialized results that already match the request base params
        my_results_to_display = self.filter_existing_results(mapgrid_instance)  # [ResultItem]
        print('Found %d requests already saved' % len(my_results_to_display))

        print("----- Request matching start -----")
        # TODO Lookup for a more efficient algorithm, esp for long lists
        my_request_container = google_parameters.RequestGroupContainer.shallow_copy(
            strictrequest_container)  # RequestGroupContainer
        print("Matching %d requests with %d results" % (len(strictrequest_container), len(my_results_to_display)))
        nb_req_found = 0
        for req in strictrequest_container.split():  # request_item_params
            is_req_found = False
            for res in my_results_to_display:
                if req.is_match(res.request_item_params):
                    is_req_found = True
                    nb_req_found += 1
                    break
            if not is_req_found:
                my_request_container.append([req.var_point])
        print("Found %d/%d matching results" % (nb_req_found, len(strictrequest_container)))
        print("------ Request matching end ------")

        print("----- GoogleAPI request start -----")
        # TODO properly catch exceptions raised by do_request()
        request_result_items = []
        if self.do_request:
            print("There are %d atomic requests to perform" % len(my_request_container))
            request_result_items.extend(self.service.do_request(my_request_container))  # [ResultItem]
            print("Found %d/%d results" % (len(request_result_items), len(my_request_container)))
            self.all_results_list.import_items(request_result_items)
            my_results_to_display.extend(request_result_items)
        else:
            print("Request mode is deactivated: none of the %d requests will be performed" % len(my_request_container))
        print("------ GoogleAPI request end ------")

        # Set properly the colors
        serialization.ResultList.set_colors(my_results_to_display, 8)

        my_results_to_display = self.substitute_geocode_latlng(my_results_to_display)

        # Not used
        # outputResultName = self.all_results_list.serialize(self.results_dir, "result", ".csv")
        # outputGeocodeName = self.geocode_list.serialize(self.geocode_dir, "geocode", ".csv")

        return strictrequest_container.base_params.fixed_point, my_results_to_display  # ([Lat,Lng],[ResultItem])

    def markers_gmaps(self, mapgrid_instance):
        (center, my_results_to_display) = self.get_data_to_display(mapgrid_instance)
        if not my_results_to_display:
            print("Nothing to display")
            return

        # Try to use only the get_data_to_display output from here...
        print("----- Map build start ----")
        out_map = js_map_generator.JSMap(mapgrid_instance.request_base_params.fixed_point[0],
                                         mapgrid_instance.request_base_params.fixed_point[1],
                                         self.zoom_level)
        print("Writing %d results markers" % (len(my_results_to_display)))
        out_map.display_result_items(my_results_to_display)
        map_name = my_io.MyIO.get_unique_name(self.out_dir, "map", ".html")
        out_map.draw(map_name)
        print("Map file generated at %s" % map_name)
        print("Browser will try to open: 'file://%s'" % path.abspath(map_name))
        webbrowser.open_new_tab("file://" + path.abspath(map_name))
        print("------ Map build end -----")

        # Display.voronoiStandalone(my_results_to_display, 0.05)

    def regions_gmaps(self, mapgrid_instance, tolerance):
        (center, my_results_to_display) = self.get_data_to_display(mapgrid_instance)
        if not my_results_to_display:
            print("Nothing to display")
            return

        (min_c, max_c, v_regions) = DisplayUtils.get_voronoi_regions(my_results_to_display, tolerance)
        if not v_regions:
            print("No data to display")
            print("------ Diplay end ------")
            return

        # Try to use only the get_data_to_display output from here...
        print("----- Map build start ----")
        out_map = js_map_generator.JSMap(mapgrid_instance.request_base_params.fixed_point[0],
                                         mapgrid_instance.request_base_params.fixed_point[1],
                                         self.zoom_level)
        out_map.display_result_regions(v_regions)
        map_name = my_io.MyIO.get_unique_name(self.out_dir, "map", ".html")
        out_map.draw(map_name)
        print("Map file generated at %s" % map_name)
        print("Browser will try to open: 'file://%s'" % path.abspath(map_name))
        webbrowser.open_new_tab("file://" + path.abspath(map_name))
        print("------ Map build end -----")


class DisplayUtils:
    def __init__(self):
        return

    @staticmethod
    def get_voronoi_regions(full_results, tolerance):  # [ResultItem],float
        output = []
        markers_latlng = []  # [[Lat,Lng]]
        print("----- Voronoi start -----")
        for result in full_results:
            markers_latlng.append(result.var_point)
        print("Markers found: %d" % len(markers_latlng))
        print("Computing Voronoi regions")
        voronoi_data = VoronoiTess(markers_latlng)
        max_c = np.amax(voronoi_data.points, 0)  # [Lat,Lng]
        min_c = np.amin(voronoi_data.points, 0)  # [Lat,Lng]
        excluded_count = 0
        for v_idx in range(0, len(voronoi_data.vertices)):
            vertex = voronoi_data.vertices[v_idx]
            if not (DisplayUtils.check_point_in_circle(vertex, min_c, max_c, tolerance)):
                excluded_count += 1
                # print("Excluded vertex #%d: %s" % (v_idx, vertex))
        if len(full_results) != len(voronoi_data.points):
            print("Major error - #Markers: %d | #VoronoiPoints: %d" % (len(full_results), len(voronoi_data.points)))
            print("------ Voronoi end ------")
            return
        print("Total vertices excluded in the process: %d" % excluded_count)
        print("Converting Voronoi polygons in actual coordinates")
        # Convert region vertex numbers into actual coordinates
        for region_idx in range(0, len(voronoi_data.regions)):
            region = voronoi_data.regions[region_idx]
            region_center = voronoi_data.points[region_idx]
            coords_latlng = []  # [[Lat,Lng]]
            for idx in region:
                if not (DisplayUtils.check_point_in_circle(voronoi_data.vertices[idx], min_c, max_c, tolerance)):
                    continue  # either we break (discard region) or continue (discard only one vertex)
                coords_latlng.append(voronoi_data.vertices[idx])
            if not coords_latlng:
                # print("Empty vertex set for index %d" % region_idx)
                continue
            # WARN By chance, the voronoi_data.points[region_idx] (the one at the 'center' of the
            # region voronoi_data.regions[region_idx]) seems to be the same that full_results[region_idx]
            # -> makes it extremely useful to retrieve the color property
            if full_results[region_idx].var_point != region_center:
                print("Major error at index %d: marker %s does not match Voronoi point %s" % (
                    region_idx, full_results[region_idx].var_point, region_center))
                print("------ Voronoi end ------")
                return
            # Remove items with default constructor values
            if full_results[region_idx].duration_value < 0:
                continue
            output.append([coords_latlng, full_results[region_idx]])  # [[[lat,lng]],resultIem]
        print("------ Voronoi end ------")
        return min_c, max_c, output

    @staticmethod
    def get_path_from_vertices(vertices):  # [[x,y]]
        if not vertices:
            return
        vertices.append(vertices[0])  # Add the first point at the end to close the path (actual value not used)
        codes = [Path.MOVETO]  # First, move the pen to the first point
        for i in range(0, len(vertices) - 2):
            codes.append(Path.LINETO)  # Than, draw a line with the next point
        codes.append(Path.CLOSEPOLY)  # Finally, close the path
        return Path(vertices, codes, closed=True)

    @staticmethod
    def check_point_in_square(point, mins, maxs, tolerance):  # [lat,lng] for 3 first params, float for the 4th
        d_lat = (maxs[0] - mins[0]) / 2
        d_lng = (maxs[1] - mins[1]) / 2
        min_lat = mins[0] - tolerance * d_lat
        max_lat = maxs[0] + tolerance * d_lat
        min_lng = mins[1] - tolerance * d_lng  # Beware : in theory, there should be a correction to tolerance = f(Lat)
        max_lng = maxs[1] + tolerance * d_lng  # Beware : in theory, there should be a correction to tolerance = f(Lat)
        if point[0] < min_lat:
            return False
        elif point[0] > max_lat:
            return False
        elif point[1] < min_lng:
            return False
        elif point[1] > max_lng:
            return False
        else:
            return True

    @staticmethod
    def check_point_in_circle(point, mins, maxs, tolerance):  # [lat,lng] for 3 first params, float for the 4th
        d_lat = (maxs[0] - mins[0]) / 2
        d_lng = (maxs[1] - mins[1]) / 2
        c_lat = (maxs[0] + mins[0]) / 2
        c_lng = (maxs[1] + mins[1]) / 2
        r_lat = mapgrid.MapGridUtils.get_distance(c_lat, c_lng, c_lat + d_lat, c_lng, False)
        r_lng = mapgrid.MapGridUtils.get_distance(c_lat, c_lng, c_lat, c_lng + d_lng, False)
        r_max = max(r_lat, r_lng)
        r = mapgrid.MapGridUtils.get_distance(c_lat, c_lng, point[0], point[1], False)
        return r < r_max * (1 + tolerance)

    @staticmethod
    def test_distance_compute():
        # Load the serialized results
        all_results_list = serialization.ResultList()  # The UNIQUE ResultList
        intput_name = my_io.MyIO.get_most_recent_from_template(abspath + "/results", "result")
        # Where the ResultList was stored
        all_results_list.import_items(serialization.ResultList.deserialize(intput_name))

        for result in all_results_list.items:
            d_simple = mapgrid.MapGridUtils.get_distance(result.originLatLng[0], result.originLatLng[1],
                                                         result.destinationLatLng[0], result.destinationLatLng[1], True)
            d_exact = mapgrid.MapGridUtils.get_distance(result.originLatLng[0], result.originLatLng[1],
                                                        result.destinationLatLng[0], result.destinationLatLng[1], False)
            d_google = result.distanceValue / 1000.0
            print("Simple = %f | Exact = %f | Google (%s) = %f" % (d_simple, d_exact, result.mode, d_google))
