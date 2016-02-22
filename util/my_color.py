import colorsys
import math


__author__ = 'adrien'

# NOTE colorsys functions are on the [0,1] interval -> some mult/div by 256 to perform


class MyColor:
    farColorRGB = [210, 21, 0]  # RGB
    nearColorRGB = [75, 191, 0]  # RGB

    # colorsys.rgb_to_hsv(210.0/256,21.0/256,0)
    farColorHSV = [0.016666666666666663, 1.0, 0.8203125]
    # colorsys.rgb_to_hsv(75.0/256, 191.0/256, 0)
    nearColorHSV = [0.26788830715532286, 1.0, 0.74609375]

    @staticmethod
    def getColorRGB(value, reference, nbSteps=0):  # 0 <-> continuous
        factor = float(value) / reference
        if (nbSteps > 0):
            factor = round(factor * nbSteps, 0) / nbSteps
        outputRGB = []
        for cIndex in range(0, 3):
            outputRGB.append((1 - factor) * MyColor.nearColorRGB[cIndex] + (factor) * MyColor.farColorRGB[cIndex])
        return outputRGB

    @staticmethod
    def getColorHSV(value, reference, nbSteps=0):  # 0 <-> continuous
        factor = float(value) / reference
        if (nbSteps > 0):
            factor = round(factor * nbSteps, 0) / nbSteps
        outputHSV = []
        for cIndex in range(0, 3):
            outputHSV.append((1 - factor) * MyColor.nearColorHSV[cIndex] + (factor) * MyColor.farColorHSV[cIndex])
        outputRGB = colorsys.hsv_to_rgb(outputHSV[0], outputHSV[1], outputHSV[2])
        # print "HSV: %f,%f,%f" % (outputHSV[0], outputHSV[1], outputHSV[2])
        # print "RGB: %f,%f,%f" % (256*outputRGB[0],256*outputRGB[1],256*outputRGB[2])
        return [256 * outputRGB[0], 256 * outputRGB[1], 256 * outputRGB[2]]

    @staticmethod
    def colorAsHexString(rgb):
        return str(hex(1 * 256 * 256 * 256 + int(math.floor(rgb[0])) * 256 * 256 + int(math.floor(rgb[1])) * 256 + int(
            math.floor(rgb[2]))))[3:]
        # return str(hex(1 * 256 * 256 * 256 + int(rgb[0]) * 256 * 256 + int(rgb[1]) * 256 + int(rgb[2])))[3:]

    @staticmethod
    def farColorAsHexString():
        return MyColor.colorAsHexString(MyColor.farColorRGB)

    @staticmethod
    def nearColorAsHexString():
        return MyColor.colorAsHexString(MyColor.nearColorRGB)
