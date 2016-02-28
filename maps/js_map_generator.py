from util import my_io

__author__ = 'ielemin'


class JSMap:
    def __init__(self, center_lat, center_lng, zoom):
        self.center = (float(center_lat), float(center_lng))
        self.zoom = int(zoom)
        self.paths = []
        self.points = []
        # self.coloricon = "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=<title>|<color>"
        self.color_icon = "http://chart.apis.google.com/chart?chst=d_bubble_text_small&chld=bb|<title>|<color>|000000"

    # From me
    def add_result_item(self, item):  # ResultItem
        if item.distanceValue >= 0:
            self.points.append(item)

    # From me
    def display_result_items(self, res):  # [ResultItem]
        for rItem in res:
            self.add_result_item(rItem)

    # From me
    def display_result_regions(self, res):  # [[[lat,lng]],resultItem]
        for rReg in res:
            self.paths.append((rReg[0], rReg[1]))

    # create the html file which inlcude one google map and all points and paths
    def draw(self, htmlfile):
        f = my_io.MyIO.get_file_write(htmlfile)
        # f = open(htmlfile, 'w')
        f.write('<html>\n')
        f.write('<head>\n')
        f.write('<meta name="viewport" content="initial-scale=1.0, user-scalable=no" />\n')
        f.write('<meta http-equiv="content-type" content="text/html; charset=UTF-8"/>\n')
        f.write('<title>Google JSMap </title>\n')
        f.write('<script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script>\n')
        f.write('<script type="text/javascript">\n')
        self.set_globals(f)
        self.fnc_toggleiw(f)
        self.fnc_calcroute(f)
        f.write('function initialize() {\n')
        self.init_map(f)

        self.draw_points(f)
        self.draw_paths(f, self.paths)
        f.write('}\n')
        f.write('</script>\n')
        f.write('</head>\n')
        f.write('<body style="margin:0px; padding:0px;" onload="initialize()">\n')
        f.write('\t<div id="map_canvas" style="width: 100%; height: 100%;"></div>\n')
        f.write('</body>\n')
        f.write('</html>\n')
        f.close()

    def draw_points(self, f):
        for pointIndex in range(0, len(self.points)):
            point = self.points[pointIndex]
            self.draw_point(f, point, pointIndex)

    def draw_paths(self, f, paths):
        for pathIndex in range(0, len(paths)):
            path = paths[pathIndex]
            self.draw_polygon(f, path[0], path[1], pathIndex)

    #############################################
    # # # # # # Low level Map Drawing # # # # # #
    #############################################

    @staticmethod
    def set_globals(f):
        f.write('var transitLayer = new google.maps.TransitLayer();\n')
        f.write("var infowindow = new google.maps.InfoWindow({content: 'empty'});\n")
        f.write("var directionsService = new google.maps.DirectionsService();\n")
        f.write("var directionsDisplay = new google.maps.DirectionsRenderer();\n")
        f.write('\n')

    @staticmethod
    def fnc_toggleiw(f):
        f.write('function toggleIW(infowindow, text, map, position) {\n')
        f.write('\tinfowindow.setContent(text)\n')
        f.write('\tinfowindow.setPosition(position)\n')
        f.write('\tinfowindow.open(map);\n')
        f.write('}\n')
        f.write('\n')

    @staticmethod
    def fnc_calcroute(f):
        f.write('function calcRoute(origin, destination, mode, units) {\n')
        f.write('\tvar request = {\n')
        f.write('\t\torigin: origin,\n')
        f.write('\t\tdestination: destination,\n')
        # TODO following values should not be manually set
        f.write('\t\ttravelMode: google.maps.TravelMode.TRANSIT,\n')
        f.write('\t\tunitSystem: google.maps.UnitSystem.METRIC};\n')
        # TODO use the request time (by default it recomputes the route at call time)
        # specify transitOption.departureTime (or arrival) in the request
        f.write('\tdirectionsService.route(request, function(response, status) {\n')
        f.write('\tif (status != google.maps.DirectionsStatus.OK) {\n')
        f.write('\t\talert("Request status is: "+status);\n')
        f.write('\t\talert("Origin was: "+request.origin);\n')
        f.write('\t\talert("Destination was: "+request.destination);}\n')
        f.write('\telse {\n')
        f.write('\t\tdirectionsDisplay.setDirections(response);}\n')
        f.write('\t});\n')
        f.write('}\n')
        f.write('\n')

    def init_map(self, f):
        f.write('var centerlatlng = new google.maps.LatLng(%f, %f);\n' % (self.center[0], self.center[1]))
        f.write('var myOptions = {\n')
        f.write('\tzoom: %d,\n' % self.zoom)
        f.write('\tcenter: centerlatlng,\n')
        f.write('\tmapTypeId: google.maps.MapTypeId.ROADMAP};\n')
        f.write('var rendererMarkerOptions = {\n')
        f.write('\tzIndex: 999999};\n')
        f.write('var rendererPolylineOptions = {\n')
        f.write('\tzIndex: 999999};\n')
        f.write('var rendererOptions = {\n')
        f.write('\tpreserveViewport: true,\n')
        f.write('\tsuppressInfoWindows: false,\n')
        f.write('\tmarkerOptions: rendererMarkerOptions,\n')
        f.write('\tpolylineOptions: rendererPolylineOptions};\n')
        # TODO also display the 'direction' details (e.g. start and end addresses, etc.)
        f.write('\n')
        f.write('var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);\n')
        f.write('transitLayer.setMap(map);\n')
        f.write('directionsDisplay.setMap(map);\n')
        f.write('directionsDisplay.setOptions(rendererOptions);\n')
        f.write('\n')
        f.write('\n')

    def draw_point(self, f, res, index):  # res: ResultItem
        lat = res.var_point[0]
        lon = res.var_point[1]
        color = res.color_as_hex_string
        title = res.title
        text = res.text

        marker_name = "marker%d" % index
        center_name = "center%d" % index
        f.write('\t\tvar %s = new google.maps.LatLng(%f, %f);\n' % (center_name, lat, lon))
        f.write('\t\tvar img = new google.maps.MarkerImage(\'%s\');\n' % (
            self.color_icon.replace('<color>', color).replace('<title>', title)))
        f.write('\t\tvar %s = new google.maps.Marker({\n' % marker_name)
        f.write('\t\t\tmap: map,\n')
        f.write('\t\t\ttitle: "%s",\n' % title)
        f.write('\t\t\ticon: img,\n')
        f.write('\t\t\tposition: %s,\n' % center_name)
        # f.write('\t\t\tanimation: google.maps.animation.DROP,\n')
        f.write('\t\t\tdraggable: false\n')
        f.write('\t\t});\n')
        f.write(
            "\t\tnew google.maps.event.addListener(%s, 'click', function() {toggleIW(infowindow, '%s', map, %s);});\n" % (
                marker_name, text, center_name))
        f.write("\t\tnew google.maps.event.addListener(%s, 'rightclick', function() {%s.setMap(null);});\n" % (
            marker_name, marker_name))
        # f.write("\t\tnew google.maps.event.addListener(%s, 'dragend', function(){searchMarkerCoords(%s,
        # infowindow);});\n" % (marker_name,marker_name))
        f.write('\n')

    # TODO do not generate explicitly the JS, but do a common JS function that loops over a table of values

    @staticmethod
    def draw_polygon(f, path, res, index):  # f:[[Lat,Lng]], res:ResultItem
        fill_color = res.color_as_hex_string
        # text = res.text
        center = res.var_point

        clickable = True
        geodesic = True
        # fill_color="000000"
        fill_opacity = 0.8
        stroke_color = "FFFFFF"
        stroke_opacity = 0.0
        stroke_weight = 1
        z_index = 1

        coords_name = "coords%d" % index
        f.write('var %s = [\n' % coords_name)
        for coordinate in path:
            f.write('\tnew google.maps.LatLng(%f, %f),\n' % (coordinate[0], coordinate[1]))
        f.write('];\n')
        center_name = "center%d" % index
        f.write('var %s = new google.maps.LatLng(%f, %f);\n' % (center_name, center[0], center[1]))
        polygon_name = "polygon%d" % index
        f.write('var %s = new google.maps.Polygon({\n' % polygon_name)
        f.write('\tclickable: %s,\n' % (str(clickable).lower()))
        f.write('\tgeodesic: %s,\n' % (str(geodesic).lower()))
        f.write('\tfillColor: "#%s",\n' % fill_color)
        f.write('\tfillOpacity: %f,\n' % fill_opacity)
        f.write('\tpaths: %s,\n' % coords_name)
        f.write('\tstrokeColor: "#%s",\n' % stroke_color)
        f.write('\tstrokeOpacity: %f,\n' % stroke_opacity)
        f.write('\tstrokeWeight: %d,\n' % stroke_weight)
        f.write('\tzIndex: %d\n' % z_index)
        f.write('});\n')
        f.write('new google.maps.event.addListener(%s, "click", function() {\n' % polygon_name)
        # f.write('\ttoggleIW(infowindow, \'%s\', map, %s);\n' % (res.text, center_name))  # be careful with " in text
        # text = "Gridpoint: %s | DMatrix address: %s | DMatrix geocode: %s" % ("toto",res.origin_geocode,res.origin_latlng)
        # ungeocode(oLatLng) should be oGeocode ; but res.origin_latlng has been replaced by geocode(oGeocode), no ?
        text = "Zone #%d" % index
        f.write('\ttoggleIW(infowindow, \'%s\', map, %s);\n' % (text, center_name))
        f.write(
            '\tcalcRoute("%s","%s","%s","%s");\n' % (res.origin_geocode, res.destination_geocode, "transit", "metric"))
        f.write('});\n')
        f.write('new google.maps.event.addListener(%s, "mouseover", function(){\n' % polygon_name)
        f.write('\tthis.setOptions({fill_opacity:"%s"});\n' % (max(1, 1.2 * fill_opacity)))
        f.write('});\n')
        f.write('new google.maps.event.addListener(%s, "mouseout", function(){\n' % polygon_name)
        f.write('\tthis.setOptions({fill_opacity:"%s"});\n' % fill_opacity)
        f.write('});\n')
        # TODO : on 'click', also highlight the cell ; on 'clickelsewhere' un highlight it
        # TODO on 'rightclick' or 'elsewhere' : remove InfoWindow & hide direction (or hide direction on IW close event)
        f.write("%s.setMap(map);\n" % polygon_name)
        f.write('\n\n')
