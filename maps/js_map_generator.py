__author__ = 'adrien'

from util import my_io

class JSMap:
    def __init__(self, centerLat, centerLng, zoom):
        self.center = (float(centerLat), float(centerLng))
        self.zoom = int(zoom)
        self.paths = []
        self.points = []
        # self.coloricon = "http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=<title>|<color>"
        self.coloricon = "http://chart.apis.google.com/chart?chst=d_bubble_text_small&chld=bb|<title>|<color>|000000"

    # From me
    def addResultItem(self, item):  # ResultItem
        if item.distanceValue >= 0:
            self.points.append(item)

    # From me
    def displayResultItems(self, res):  # [ResultItem]
        for rItem in res:
            self.addResultItem(rItem)

    # From me
    def displayResultRegions(self, res):  # [[[lat,lng]],resultItem]
        for rReg in res:
            self.paths.append((rReg[0], rReg[1]))

    # create the html file which inlcude one google map and all points and paths
    def draw(self, htmlfile):
        f = my_io.myIO.GetFileWrite(htmlfile)
        # f = open(htmlfile, 'w')
        f.write('<html>\n')
        f.write('<head>\n')
        f.write('<meta name="viewport" content="initial-scale=1.0, user-scalable=no" />\n')
        f.write('<meta http-equiv="content-type" content="text/html; charset=UTF-8"/>\n')
        f.write('<title>Google JSMap </title>\n')
        f.write('<script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script>\n')
        f.write('<script type="text/javascript">\n')
        self.setglobals(f)
        self.fnc_toggleiw(f)
        self.fnc_calcroute(f)
        f.write('function initialize() {\n')
        self.initmap(f)

        self.drawpoints(f)
        self.drawpaths(f, self.paths)
        f.write('}\n')
        f.write('</script>\n')
        f.write('</head>\n')
        f.write('<body style="margin:0px; padding:0px;" onload="initialize()">\n')
        f.write('\t<div id="map_canvas" style="width: 100%; height: 100%;"></div>\n')
        f.write('</body>\n')
        f.write('</html>\n')
        f.close()

    def drawpoints(self, f):
        for pointIndex in range(0, len(self.points)):
            point = self.points[pointIndex]
            self.drawpoint(f, point, pointIndex)

    def drawpaths(self, f, paths):
        for pathIndex in range(0, len(paths)):
            path = paths[pathIndex]
            self.drawPolygon(f, path[0], path[1], pathIndex)


    #############################################
    # # # # # # Low level Map Drawing # # # # # #
    #############################################
    def setglobals(self, f):
        f.write('var transitLayer = new google.maps.TransitLayer();\n')
        f.write("var infowindow = new google.maps.InfoWindow({content: 'empty'});\n")
        f.write("var directionsService = new google.maps.DirectionsService();\n")
        f.write("var directionsDisplay = new google.maps.DirectionsRenderer();\n")
        f.write('\n')

    def fnc_toggleiw(self, f):
        f.write('function toggleIW(infowindow, text, map, position) {\n')
        f.write('\tinfowindow.setContent(text)\n')
        f.write('\tinfowindow.setPosition(position)\n')
        f.write('\tinfowindow.open(map);\n')
        f.write('}\n')
        f.write('\n')

    def fnc_calcroute(self, f):
        f.write('function calcRoute(origin, destination, mode, units) {\n')
        f.write('\tvar request = {\n')
        f.write('\t\torigin: origin,\n')
        f.write('\t\tdestination: destination,\n')
        # TODO following values should not be manually set
        f.write('\t\ttravelMode: google.maps.TravelMode.TRANSIT,\n')
        f.write('\t\tunitSystem: google.maps.UnitSystem.METRIC};\n')
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

    def initmap(self, f):
        f.write('var centerlatlng = new google.maps.LatLng(%f, %f);\n' % (self.center[0], self.center[1]))
        f.write('var myOptions = {\n')
        f.write('\tzoom: %d,\n' % (self.zoom))
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

    def drawpoint(self, f, res, index):  # res: ResultItem
        lat = res.varPoint[0]
        lon = res.varPoint[1]
        color = res.colorAsHexString
        title = res.title
        text = res.text

        markerName = "marker%d" % index
        centerName = "center%d" % index
        f.write('\t\tvar %s = new google.maps.LatLng(%f, %f);\n' % (centerName, lat, lon))
        f.write('\t\tvar img = new google.maps.MarkerImage(\'%s\');\n' % (
            self.coloricon.replace('<color>', color).replace('<title>', title)))
        f.write('\t\tvar %s = new google.maps.Marker({\n' % markerName)
        f.write('\t\t\tmap: map,\n')
        f.write('\t\t\ttitle: "%s",\n' % title)
        f.write('\t\t\ticon: img,\n')
        f.write('\t\t\tposition: %s,\n' % centerName)
        # f.write('\t\t\tanimation: google.maps.animation.DROP,\n')
        f.write('\t\t\tdraggable: false\n')
        f.write('\t\t});\n')
        f.write(
            "\t\tnew google.maps.event.addListener(%s, 'click', function() {toggleIW(infowindow, '%s', map, %s);});\n" % (
                markerName, text, centerName))
        f.write("\t\tnew google.maps.event.addListener(%s, 'rightclick', function() {%s.setMap(null);});\n" % (
            markerName, markerName))
        # f.write("\t\tnew google.maps.event.addListener(%s, 'dragend', function(){searchMarkerCoords(%s, infowindow);});\n" % (markerName,markerName))
        f.write('\n')

    # TODO do not generate explicitly the JS, but do a common JS function that loops over a table of values

    def drawPolygon(self, f, path, res, index):  # f:[[Lat,Lng]], res:ResultItem
        fillColor = res.colorAsHexString
        # text = res.text
        center = res.varPoint

        clickable = True
        geodesic = True
        # fillColor="000000"
        fillOpacity = 0.8
        strokeColor = "FFFFFF"
        strokeOpacity = 0.0
        strokeWeight = 1

        coordsName = "coords%d" % index
        f.write('var %s = [\n' % coordsName)
        for coordinate in path:
            f.write('\tnew google.maps.LatLng(%f, %f),\n' % (coordinate[0], coordinate[1]))
        f.write('];\n')
        centerName = "center%d" % index
        f.write('var %s = new google.maps.LatLng(%f, %f);\n' % (centerName, center[0], center[1]))
        polygonName = "polygon%d" % index
        f.write('var %s = new google.maps.Polygon({\n' % polygonName)
        f.write('\tclickable: %s,\n' % (str(clickable).lower()))
        f.write('\tgeodesic: %s,\n' % (str(geodesic).lower()))
        f.write('\tfillColor: "#%s",\n' % (fillColor))
        f.write('\tfillOpacity: %f,\n' % (fillOpacity))
        f.write('\tpaths: %s,\n' % coordsName)
        f.write('\tstrokeColor: "#%s",\n' % (strokeColor))
        f.write('\tstrokeOpacity: %f,\n' % (strokeOpacity))
        f.write('\tstrokeWeight: %d\n' % (strokeWeight))
        f.write('});\n')
        f.write('new google.maps.event.addListener(%s, "click", function() {\n' % polygonName)
        # f.write('\ttoggleIW(infowindow, \'%s\', map, %s);\n' % (res.text, centerName))  # be careful with " in text
        # text = "Gridpoint: %s | DMatrix address: %s | DMatrix geocode: %s" % ("toto",res.originGeocode,res.originLatLng)
        # ungeocode(oLatLng) should be oGeocode ; but res.originLatLng has been replaced by geocode(oGeocode), no ?
        text = "Zone #%d" % index
        f.write('\ttoggleIW(infowindow, \'%s\', map, %s);\n' % (text, centerName))
        f.write(
            '\tcalcRoute("%s","%s","%s","%s");\n' % (res.originGeocode, res.destinationGeocode, "transit", "metric"))
        f.write('});\n')
        f.write('new google.maps.event.addListener(%s, "mouseover", function(){\n' % polygonName)
        f.write('\tthis.setOptions({fillOpacity:"%s"});\n' % (max(1, 1.2 * fillOpacity)))
        f.write('});\n')
        f.write('new google.maps.event.addListener(%s, "mouseout", function(){\n' % polygonName)
        f.write('\tthis.setOptions({fillOpacity:"%s"});\n' % fillOpacity)
        f.write('});\n')
        # TODO : on 'click', also highlight the cell ; on 'clickelsewhere' un highlight it
        # TODO on 'rightclick' or 'elsewhere' : remove InfoWindow & hide direction (or hide direction on IW close event)
        f.write("%s.setMap(map);\n" % polygonName)
        f.write('\n\n')