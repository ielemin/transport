from util import my_color
from util import my_io
from data import results


class ResultList:
    def __init__(self):
        self.items = []  # [ResultItem]

    def importItems(self, items):
        if not (items):
            return
        self.items.extend(items)

    def toString(self):
        print("---- Results start ----")
        for index in range(0, len(self.items)):
            print("Path #%d" % index)
            item = self.items[index]
            print("Origin: %s" % item.originGeocode)
            print("Destination: %s" % item.destinationGeocode)
            print("Travel time: %s (%d s)" % (item.durationText, item.durationValue))
            print("Travel distance: %s (%d m)" % (item.distanceText, item.distanceValue))
        print("----- Results end -----")

    @staticmethod
    def SetColors(items, nbSteps):  # [ResultItem]
        maxDuration = 0
        maxDistance = 0
        # First, compute the max values
        if not (items): return
        for item in items:
            durationValue = item.durationValue
            distanceValue = item.distanceValue
            if (durationValue > maxDuration):
                maxDuration = durationValue
            if (distanceValue > maxDistance):
                maxDistance = distanceValue
        # Second, set the colors
        for item in items:
            # item.color = myColor.MyColor.MyColor.getColorRGB(item.durationValue, maxDuration)
            item.color = my_color.MyColor.getColorHSV(item.durationValue, maxDuration, nbSteps)

    def Serialize(self, filePath, fileName, ext):
        print("----- Serialization start -----")
        fileFullName = my_io.myIO.GetUniqueName(filePath, fileName, ext)
        print("Serializing results to %s" % (fileFullName))
        f = my_io.myIO.GetFileWrite(fileFullName)
        for index in range(0, len(self.items)):
            item = self.items[index]
            line = "%d" % item.reqTimestamp
            line += "\t%s" % item.originLatLng
            line += "\t%s" % item.destinationLatLng
            line += "\t%s" % item.isDestinationFixed
            line += "\t%d" % item.fixedTime
            line += "\t%s" % item.mode
            line += "\t%s" % item.originGeocode
            line += "\t%s" % item.destinationGeocode
            line += "\t%s" % item.distanceText
            line += "\t%s" % item.distanceValue
            line += "\t%s" % item.durationText
            line += "\t%s" % item.durationValue
            line += "\n"
            f.write(line)
        f.close()
        print("%d items serialized" % len(self.items))
        print("------ Serialization end ------")
        return fileFullName

    # There should be only ONE ResultList, but no easy singleton in python
    # -> to prevent creating two different ResultList,
    # return an array of items and append them to the ResultList
    @staticmethod
    def Deserialize(fileFullName):
        print("----- Deserialization start -----")
        print("Deserializing results from %s" % (fileFullName))
        f = my_io.myIO.GetFileRead(fileFullName)
        if not (f): return
        items = []
        errors = 0
        for line in f:
            cLine = line[:-1].split('\t')  # -1 removes the \n
            if len(cLine) < 12: continue
            rTimestamp = int(cLine[0])
            oLatLng = my_io.myIO.u_to_floatArray(cLine[1])
            dLatLng = my_io.myIO.u_to_floatArray(cLine[2])
            dFixed = bool(cLine[3])
            aTime = int(cLine[4])
            mode = str(cLine[5])
            oGeo = cLine[6]
            dGeo = cLine[7]
            diTxt = str(cLine[8])
            diVal = int(cLine[9])
            duTxt = str(cLine[10])
            duVal = int(cLine[11])
            if 'km' in duTxt:  # if columns have been accidentally switched
                diTxt, diVal, duTxt, duVal = duTxt, duVal, diTxt, diVal
                errors += 1
            items.append(
                results.ResultItem(rTimestamp, oLatLng, dLatLng, dFixed, aTime, mode, oGeo, dGeo, diTxt, diVal, duTxt, duVal))
        f.close()
        print("%d valid items deserialized" % len(items))
        print("Possible errors: %d" % errors)
        print("------ Deserialization end ------")
        return items

    def GetByRequest(self, req):  # RequestItemParams
        for item in self.items:  # ResultItem
            if item.mode != req.baseParams.mode: continue
            if item.fixedTime != req.baseParams.fixedTime: continue
            if item.originLatLng != req.origin: continue
            if item.destinationLatLng != req.destination: continue
            return item
        return

    def __len__(self):
        return len(self.items)