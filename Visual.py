from PIL import Image, ImageDraw, ImageChops, ImageStat, ImageFilter
import math
import time

####################################
# Utility Functions
####################################

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
    
    def changeColor(self, img, srcColor, dstColor):
        colorTable = list(range(256))
        colorTable[srcColor] = dstColor
        return img.point(colorTable)
    
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

####################################
# Compare Functions
####################################
class Compare(Utility):
    IDENTITY_THRESHOLD = .985
    REFLECTION_THRESHOLD = .97
    TRANSLATION_THRESHOLD = .95
    CROSS_THRESHOLD = .95
    ROTATION_THRESHOLD = .95
    ADD_SUB_THRESHOLD = .975
    
    THRESHOLDS = {'identity' : .985,
                  'reflection' : .97,
                  'translation' : .95,
                  'cross' : .95,
                  'rotation' : .95,
                  'addSub' : .98}
    
    
    WEIGHTS = {'identity' : .05,
               'reflection' : .02,
               'translation' : .02,
               'cross' : .03,
               'rotation' : .02,
               'addSub' : .05
               }
    
    
    def __init__(self, name, srcFig, dstFig, ansCol):
        self.name = name
        self.srcFig = srcFig
        self.dstFig = dstFig
        self.ansCol = ansCol
        self.bestScore = 0
        self.bestTransform = None
        self.identity = False
        self.reflectXAxis = False
        self.reflectYAxis = False
        self.translate = False
        self.transWidth = 0
        self.transHeight = 0
        self.crossX = False
        self.crossXType = None
        self.crossY = False
        self.crossYType = None
        self.rotate = False
        self.rotateDegree = 0
        self.rotateShadow = False
        self.add = None
        self.sub = None
        
    # Simple comparison to determine if 2 images are the same
    def same(self, srcImg, dstImg):
        srcImg = Utility.centerImage(srcImg).filter(ImageFilter.GaussianBlur(3))
        dstImg = Utility.centerImage(dstImg).filter(ImageFilter.GaussianBlur(3))
        score = Utility.pixelMatch(srcImg, dstImg)
        if score > self.THRESHOLDS['identity']:
            score += self.WEIGHTS['identity']
            self.identity = True
        if score > self.bestScore:
            self.bestScore = score
            self.bestTransform = 'identity'
            return
        else:
            return
    
    # Reflect an image over the x-axis and compare
    # against the dstImg
    def reflectionXAxis(self, srcImg, dstImg):
        cpyImg = srcImg.copy()
        cpyImg = cpyImg.transpose(Image.FLIP_TOP_BOTTOM)
        score = Utility.pixelMatch(cpyImg, dstImg)
        if score > self.THRESHOLDS['reflection'] and self.tiebreaker():
            self.reflectXAxis = True
            score += self.WEIGHTS['reflection']
        if score > self.bestScore:
            self.bestScore = score
            self.bestTransform = 'reflect_x'
            return         
        else:
            return
    
    # Reflect an image over the y-axis and compare
    # against the dstImg
    def reflectionYAxis(self, srcImg, dstImg):
        cpyImg = srcImg.copy()
        cpyImg = cpyImg.transpose(Image.FLIP_LEFT_RIGHT)
        score = Utility.pixelMatch(cpyImg, dstImg)
        if score > self.THRESHOLDS['reflection'] and self.tiebreaker():
            self.reflectYAxis = True
            score += self.WEIGHTS['reflection']
        if score > self.bestScore:
            self.bestScore = score
            self.bestTransform = 'reflect_y'
            return         
        else:
            return
        
    def translation(self, srcImg, dstImg, shadow=True):
        srcBox, srcBoxWidth, srcBoxHeight = Utility.getBox(srcImg)
        dstBox, dstBoxWidth, dstBoxHeight = Utility.getBox(dstImg)
        srcCrop = srcImg.crop(srcBox)
        dstCrop = Image.new('L', (dstBoxWidth, dstBoxHeight), 0)
        translateCoords = (dstBoxWidth - srcBoxWidth, dstBoxHeight - srcBoxHeight)
        dstCrop.paste(srcCrop, translateCoords)
        if shadow:
            dstCrop.paste(srcCrop, (0,0), mask=srcCrop)
        finalImg = Image.new('L', (dstImg.size[0], dstImg.size[1]),0)
        finalImg.paste(dstCrop, (0,0))
        finalImg = Utility.centerImage(finalImg)
        dstImg = Utility.centerImage(dstImg)
        transWidth, transHeight = dstBoxWidth - srcBoxWidth, dstBoxHeight - srcBoxHeight
        score = Utility.pixelMatch(finalImg, dstImg)
        if score > self.THRESHOLDS['translation']:
            self.translate = True
            score += self.WEIGHTS['translation']
        if score > self.bestScore:
            self.bestScore = score
            self.bestTransform = 'translate'
            self.transWidth = transWidth
            self.transHeight = transHeight
            return
        else:
            return
        
    def crossXAxis(self, srcImg, dstImg):
        srcBox, srcBoxWidth, srcBoxHeight = Utility.getBox(srcImg)
        dstBox, dstBoxWidth, dstBoxHeight = Utility.getBox(dstImg)
        crossType = Utility.getCrossType(srcBoxWidth, dstBoxWidth)
        if not crossType:
            return
        else:
            pass
        left, right = Utility.splitYAxis(srcImg)
        leftBox, leftBoxWidth, leftBoxHeight = Utility.getBox(left)
        rightBox, rightBoxWidth, rightBoxHeight = Utility.getBox(right)
        leftCrop = left.crop(leftBox)
        rightCrop = right.crop(rightBox)
        dstCrop = Image.new('L', (dstBoxWidth, dstBoxHeight), 0)
        dstCrop.paste(leftCrop, (dstBoxWidth - leftBoxWidth, 0), mask=leftCrop)
        dstCrop.paste(rightCrop, (0, 0), mask=rightCrop)
        finalImg = Image.new('L', (dstImg.size[0], dstImg.size[1]),0)
        finalImg.paste(dstCrop, (0,0))
        finalImg = Utility.centerImage(finalImg)
        dstImg = Utility.centerImage(dstImg)
        score = Utility.pixelMatch(finalImg, dstImg)
        if score > self.THRESHOLDS['cross']:
            self.crossX = True
            score += self.WEIGHTS['cross']
        if score > self.bestScore:
            self.bestScore = score
            self.bestTransform = 'cross_x'
            self.crossXType = crossType
            return
        else:
            return
    
    def rotation(self, srcImg, dstImg):
        degrees = (45, 60, 72, 90, 120, 135, 144, 180, 216, 225, 240, 270, 288, 300, 315)
        bestDegreeNoShadow = 0
        bestDegreeShadow = 0
        bestScoreNoShadow = 0
        bestScoreShadow = 0
        
        for i in degrees:
            rotImg = srcImg.rotate(i)
            scoreNoShadow = Utility.pixelMatch(rotImg, dstImg)
            if scoreNoShadow > bestScoreNoShadow:
                bestScoreNoShadow = scoreNoShadow
                bestDegreeNoShadow = i
            shadowImg = Image.composite(srcImg, rotImg, mask=srcImg)
            scoreShadow = Utility.pixelMatch(shadowImg, dstImg)
            if scoreShadow > bestScoreShadow:
                bestScoreShadow = scoreShadow
                bestDegreeShadow = i
        
        if bestScoreShadow > self.THRESHOLDS['rotation'] and self.tiebreaker():
            self.rotate = True
            bestScoreShadow += self.WEIGHTS['rotation']
        if bestScoreNoShadow > self.THRESHOLDS['rotation'] and self.tiebreaker():
            self.rotate = True
            bestScoreNoShadow += self.WEIGHTS['rotation']
        
        if bestScoreShadow > bestScoreNoShadow and bestScoreShadow > self.bestScore:
            self.bestScore = bestScoreShadow
            self.bestTransform = 'rotate'
            self.rotateDegree = bestDegreeShadow
            self.rotateShadow = True
            return
        elif bestScoreNoShadow > self.bestScore:
            self.bestScore = bestScoreNoShadow
            self.bestTransform = 'rotate'
            self.rotateDegree = bestDegreeNoShadow
            return
        else:
            return
    
    def imagesToAdd(self, srcImg, dstImg):
        self.add = ImageChops.subtract(dstImg, srcImg)
    
    def imagesToSub(self, srcImg, dstImg):
        self.sub = ImageChops.subtract(srcImg, dstImg)
        
    def tiebreaker(self):
        if self.identity:
            return False
        if self.reflectXAxis or self.reflectYAxis:
            return False
        return True
    
####################################
# Generate Functions
####################################
class Generate(Utility):
    
    @staticmethod
    def reflectionXAxis(srcImg):
        return srcImg.transpose(Image.FLIP_TOP_BOTTOM)
    
    @staticmethod
    def reflectionYAxis(srcImg):
        return srcImg.transpose(Image.FLIP_LEFT_RIGHT)

    @staticmethod
    def translation(srcImg, x, y, shadow=True):
        srcBox, srcBoxWidth, srcBoxHeight = Utility.getBox(srcImg)
        dstBoxWidth, dstBoxHeight = srcBoxWidth + x, srcBoxHeight + y
        srcCrop = srcImg.crop(srcBox)
        dstCrop = Image.new('L', (dstBoxWidth, dstBoxHeight), 0)
        translateCoords = (dstBoxWidth - srcBoxWidth, dstBoxHeight - srcBoxHeight)
        dstCrop.paste(srcCrop, translateCoords)
        if shadow:
            dstCrop.paste(srcCrop, (0,0), mask=srcCrop)
        dstImg = Image.new('L', (srcImg.size[0], srcImg.size[1]),0)
        dstImg.paste(dstCrop, (0,0))
        dstImg = Utility.centerImage(dstImg)
        return dstImg
    
    @staticmethod
    def crossX(srcImg, type):
        srcImgWidth, srcImgHeight = srcImg.size[0], srcImg.size[1]
        srcBox, srcBoxWidth, srcBoxHeight = Utility.getBox(srcImg)
        left, right = Utility.splitYAxis(srcImg)
        leftBox, leftBoxWidth, leftBoxHeight = Utility.getBox(left)
        rightBox, rightBoxWidth, rightBoxHeight = Utility.getBox(right)
        leftCrop = left.crop(leftBox)
        rightCrop = right.crop(rightBox)
        dstImg = Image.new('L', (srcImgWidth, srcImgHeight),0)
        if type == 'pass-through':
            dstBoxWidth = srcBoxWidth
        else:
            dstBoxWidth = max(leftBoxWidth, rightBoxWidth)
        dstImg.paste(rightCrop, (0,0), mask=rightCrop)
        dstImg.paste(leftCrop, (dstBoxWidth - leftBoxWidth, 0), mask=leftCrop)
        return Utility.centerImage(dstImg)
    
    @staticmethod
    def rotation(srcImg, degree, shadow=False):
        dstImg = srcImg.rotate(degree)
        if shadow:
            dstImg = Image.composite(srcImg, dstImg, mask=srcImg)
        return dstImg
    
    @staticmethod
    def addSubtract(srcImg, addImg, subImg):
        dstImg = ImageChops.add(srcImg, addImg)
        dstImg = ImageChops.subtract(dstImg, subImg)
        return dstImg
    
    @staticmethod
    def addSubtractDiff(imgA, imgB):
        diffImg = ImageChops.difference(imgA, imgB)
        imgA = ImageChops.subtract(imgA, diffImg)
        imgB = ImageChops.subtract(imgB, diffImg)
        return imgA, imgB

####################################s
# Test Functions
####################################

def main():
    from Test import Problem
    BLACK = 0
    WHITE = 255
    
    problemSet = 'Basic Problems C'
    problemName = 'Basic Problem C-01'
    problemImages = {}
    problem = Problem(problemSet, problemName)
    for figName, figObj in problem.problem.figures.items():
        fh = Image.open(figObj.visualFilename)
        problemImages[figName] = Utility.blackOut(ImageChops.invert(fh.convert('L')).filter(ImageFilter.GaussianBlur(3)))
    
    figA = problemImages['A']
    figB = problemImages['B']
    figC = problemImages['C']
    figD = problemImages['D']
    figE = problemImages['E']
    figF = problemImages['F']
    figG = problemImages['G']
    figH = problemImages['H']
    ans = problemImages['4']
    
    a_c = Compare('A -> C', figA, figC)
    b_c = Compare('B -> C', figB, figC)
    
    print(Utility.pixelMatch(figD, figF))

if __name__ == '__main__':
    main()
    