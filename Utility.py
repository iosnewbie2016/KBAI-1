from PIL import Image, ImageDraw, ImageChops, ImageStat, ImageFilter
import math

class Utility:
    # Converts any pixels with 0 < color < 255 to black
    @staticmethod
    def blackOut(img):
        pixel = img.load()
        w, h = img.size
        for x in range(w):
            for y in range(h):
                if pixel[x, y] == 0:
                    continue
                elif pixel[x, y] < 255:
                    pixel[x, y] = 0
        return img
    
    # Finds the bounding box of white images and centers the 
    # image 
    @staticmethod
    def centerImage(img):
        imgBox, imgBoxWidth, imgBoxHeight = Utility.getBox(img)
        imgWidth, imgHeight = img.size
        #imgBoxWidth = imgBox[2] - imgBox[0]
        #imgBoxHeight = imgBox[3] - imgBox[1]
        centerCoords = ((imgWidth - imgBoxWidth)/2, (imgHeight - imgBoxHeight)/2)
        return ImageChops.offset(img, int(centerCoords[0] - imgBox[0]), int(centerCoords[1] - imgBox[1]))
    
    @staticmethod
    def topLeftCornerImage(img):
        imgBox, imgBoxWidth, imgBoxheight = Utility.getBox(img)
        return ImageChops.offset(img,-imgBox[0], -imgBox[1])
    
    @staticmethod
    def bottomLeftCornerImage(img):
        imgBox, imgBoxWidth, imgBoxheight = Utility.getBox(img)
        return ImageChops.offset(img, -imgBox[0], img.size[1] - imgBox[3])
    
    
    @staticmethod
    def getBox(img):
        imgBox = img.getbbox()
        if imgBox == None:
            return (0,0,184,184), 184, 184
        imgBoxWidth = imgBox[2] - imgBox[0]
        imgBoxHeight = imgBox[3] - imgBox[1]
        return imgBox, imgBoxWidth, imgBoxHeight
    
    @staticmethod
    def splitXAxis(img):
        pass
    
    @staticmethod
    def splitYAxis(img):
        width, height = img.size
        left = img.crop((0, 0, int(width/2), height))
        right = img.crop((int(width/2), 0, width, height))
        return left, right
    
    @staticmethod
    def getCrossType(srcBoxWidth, dstBoxWidth):
        if Utility.RMSE(srcBoxWidth, dstBoxWidth) < 5:
            return 'pass-through'
        elif Utility.RMSE(srcBoxWidth/2, dstBoxWidth) < 5:
            return 'merge'
        else:
            return False
    
    @staticmethod
    def RMSE(predictions, target):
        return math.sqrt((predictions - target)**2)
    
    @staticmethod
    def pixelMatch(srcImage, dstImage):
        bestScore = 0.0
        for yOffset in range(-3, 4, 2):
            for xOffset in range(-3, 4, 2):
                diffImage = ImageChops.difference(ImageChops.offset(srcImage, xOffset, yOffset), dstImage)
                pixelCount = srcImage.size[0] * srcImage.size[1]
                stats = ImageStat.Stat(diffImage)
                score = 1.0 - ((stats.sum[0] / 255.0) / pixelCount)
                bestScore = max(score, bestScore)
        return bestScore
    
    @staticmethod
    def floodFind(image, value):
        """Uses flood fill to detct regions of a color"""
        image = image.copy()
        regions = 0
        try:
            while True:
                i = list(image.getdata()).index(value)
                regions += 1
                ImageDraw.floodfill(Image, self.flat_to_xy(i, image.size[0]), regions)
        except ValueError:
                pass
            
        res = []
        for i in xrange(1, regions + 1):
            foundimage = image.point(lambda a: 255 if a == i else 0)
            bb = foundimage.getbox()
            if bb == None:
                continue
            start = (bb[0], bb[1])
            size = (bb[2] - bb[0], bb[3] - bb[1])
            foundimage = foundimage.crop(bb)
            res.append((start, size, list(foundimage.getdata())))
        return res