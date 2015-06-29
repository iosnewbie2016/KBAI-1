from PIL import Image, ImageDraw, ImageChops, ImageStat
from Test import Problem
import math
import time

####################################
# Utility Functions
####################################

# Converts any pixels with 0 < color < 255 to black
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

def changeColor(img, srcColor, dstColor):
    colorTable = list(range(256))
    colorTable[srcColor] = dstColor
    return img.point(colorTable)

#Returns the number of pixels in the image with the given color
def area(img, color):
    return img.histogram()[color]

# Finds the bounding box of white images and centers the 
# image 
def centerImage(img):
    imgBox, imgBoxWidth, imgBoxHeight = getBox(img)
    imgWidth, imgHeight = img.size
    #imgBoxWidth = imgBox[2] - imgBox[0]
    #imgBoxHeight = imgBox[3] - imgBox[1]
    centerCoords = ((imgWidth - imgBoxWidth)/2, (imgHeight - imgBoxHeight)/2)
    
    return ImageChops.offset(img, int(centerCoords[0] - imgBox[0]), int(centerCoords[1] - imgBox[1]))

def getBox(img):
    imgBox = img.getbbox()
    imgBoxWidth = imgBox[2] - imgBox[0]
    imgBoxHeight = imgBox[3] - imgBox[1]
    return imgBox, imgBoxWidth, imgBoxHeight

def splitXAxis(img):
    pass

def splitYAxis(img):
    width, height = img.size
    left = img.crop((0, 0, int(width/2), height))
    right = img.crop((int(width/2), 0, width, height))
    return left, right

def getCrossType(srcBoxWidth, dstBoxWidth):
    if RMSE(srcBoxWidth, dstBoxWidth) < 5:
        return 'pass-through'
    elif RMSE(srcBoxWidth/2, dstBoxWidth) < 5:
        return 'merge'
    else:
        return False

def RMSE(predictions, target):
    return math.sqrt((predictions - target)**2)

####################################
# BORROWED! MUST CHANGE!!!
####################################

def pixelCompare(imgA, imgB):
    # perform RMS error calculation to determine similarity
    countDiff = 0
    img1 = imgA.copy().convert('L')
    img2 = imgB.copy().convert('L')

    # loop over all image data; find the difference in pixel values,
    # square the difference, add to sum, then return square root of sum/(# of pts)
    for x,y in zip(list(img1.getdata()),list(img2.getdata())):
        countDiff += abs(x-y)**2

    return math.sqrt(countDiff/(img1.size[0]*img1.size[1]))

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
# Compare the pixel count of a given color in 2 images
# and determmine the linear coefficient
def areaFactor(srcImg, dstImg, color):
    srcArea = area(srcImg, color)
    dstArea = area(dstImg, color)
    return max(srcArea, dstArea) / min(srcArea, dstArea)

# Reflect an image over the x-axis and compare
# against the dstImg
def reflectionXAxis(srcImg, dstImg):
    cpyImg = srcImg.copy()
    cpyImg = cpyImg.transpose(Image.FLIP_TOP_BOTTOM)
    return pixelMatch(cpyImg, dstImg)

# Reflect an image over the y-axis and compare
# against the dstImg
def reflectionYAxis(srcImg, dstImg):
    cpyImg = srcImg.copy()
    cpyImg = cpyImg.transpose(Image.FLIP_LEFT_RIGHT)
    return pixelMatch(cpyImg, dstImg)

# Simple comparison to determine if 2 images are the same
def same(srcImg, dstImg):
    return pixelMatch(srcImg, dstImg)
    
def translation(srcImg, dstImg, shadow=False):
    srcBox, srcBoxWidth, srcBoxHeight = getBox(srcImg)
    dstBox, dstBoxWidth, dstBoxHeight = getBox(dstImg)
    srcCrop = srcImg.crop(srcBox)
    dstCrop = Image.new('L', (dstBoxWidth, dstBoxHeight), 0)
    translateCoords = (dstBoxWidth - srcBoxWidth, dstBoxHeight - srcBoxHeight)
    dstCrop.paste(srcCrop, translateCoords)
    if shadow:
        dstCrop.paste(srcCrop, (0,0), mask=srcCrop)
    finalImg = Image.new('L', (dstImg.size[0], dstImg.size[1]),0)
    finalImg.paste(dstCrop, (0,0))
    finalImg = centerImage(finalImg)
    dstImg = centerImage(dstImg)
    transWidth, transHeight = dstBoxWidth - srcBoxWidth, dstBoxHeight - srcBoxHeight
    return pixelMatch(finalImg, dstImg), transWidth, transHeight
    
def crossX(srcImg, dstImg):
    srcBox, srcBoxWidth, srcBoxHeight = getBox(srcImg)
    dstBox, dstBoxWidth, dstBoxHeight = getBox(dstImg)
    crossType = getCrossType(srcBoxWidth, dstBoxWidth)
    if not crossType:
        return 0.0, None
    else:
        pass
    left, right = splitYAxis(srcImg)
    leftBox, leftBoxWidth, leftBoxHeight = getBox(left)
    rightBox, rightBoxWidth, rightBoxHeight = getBox(right)
    leftCrop = left.crop(leftBox)
    rightCrop = right.crop(rightBox)
    dstCrop = Image.new('L', (dstBoxWidth, dstBoxHeight), 0)
    dstCrop.paste(leftCrop, (dstBoxWidth - leftBoxWidth, 0), mask=leftCrop)
    dstCrop.paste(rightCrop, (0, 0), mask=rightCrop)
    finalImg = Image.new('L', (dstImg.size[0], dstImg.size[1]),0)
    finalImg.paste(dstCrop, (0,0))
    finalImg = centerImage(finalImg)
    dstImg = centerImage(dstImg)
    return pixelMatch(finalImg, dstImg), crossType

def rotation(srcImg, dstImg):
    degrees = (45, 60, 72, 90, 120, 135, 144, 180, 216, 225, 240, 270, 288, 300, 315)
    bestDegreeNoShadow = 0
    bestDegreeShadow = 0
    bestScoreNoShadow = 0
    bestScoreShadow = 0
    
    #startTime = time.time()
    for i in degrees:
        rotImg = srcImg.rotate(i)
        scoreNoShadow = pixelMatch(rotImg, dstImg)
        if scoreNoShadow > bestScoreNoShadow:
            bestScoreNoShadow = scoreNoShadow
            bestDegreeNoShadow = i
        shadowImg = Image.composite(srcImg, rotImg, mask=srcImg)
        if i == 360 - 73:
            shadowImg.show()
            rotImg.show()
            dstImg.show()
        scoreShadow = pixelMatch(shadowImg, dstImg)
        if scoreShadow > bestScoreShadow:
            bestScoreShadow = scoreShadow
            bestDegreeShadow = i
    """
    endTime = time.time()
    print('Total Time: {}'.format(endTime - startTime))
    print('Best Score Shadow: {}, Degree: {}'.format(bestScoreShadow, bestDegreeShadow))
    print('Best Score No Shadow: {}, Degree: {}'.format(bestScoreNoShadow, bestDegreeNoShadow))
    """
    if bestScoreShadow > bestScoreNoShadow:
        shadow = True
        return bestScoreShadow, bestDegreeShadow, shadow
    else:
        shadow = False
        return bestScoreNoShadow, bestDegreeNoShadow, shadow
 
def addSubtract2(srcImg, dstImg):
    alpha = .75
    add = False
    subtract = False
    subtractColor = 63
    addColor = 191
    
    blendImg = Image.blend(srcImg, dstImg, alpha)
    for count, color in blendImg.getcolors():
        if color == subtractColor:
            pass
        elif color == addColor:
            pass
        else:
            pass

def imagesToAdd(srcImg, dstImg):
    return ImageChops.subtract(dstImg, srcImg)

def imagesToSub(srcImg, dstImg):
    return ImageChops.subtract(srcImg, dstImg)
    
####################################
# Generate Functions
####################################
def generateTranslation(srcImg, x, y, shadow=False):
    srcBox, srcBoxWidth, srcBoxHeight = getBox(srcImg)
    dstBoxWidth, dstBoxHeight = srcBoxWidth + x, srcBoxHeight + y
    srcCrop = srcImg.crop(srcBox)
    dstCrop = Image.new('L', (dstBoxWidth, dstBoxHeight), 0)
    translateCoords = (dstBoxWidth - srcBoxWidth, dstBoxHeight - srcBoxHeight)
    dstCrop.paste(srcCrop, translateCoords)
    if shadow:
        dstCrop.paste(srcCrop, (0,0), mask=srcCrop)
    dstImg = Image.new('L', (srcImg.size[0], srcImg.size[1]),0)
    dstImg.paste(dstCrop, (0,0))
    dstImg = centerImage(dstImg)
    return dstImg

def generateCrossX(srcImg, type):
    srcImgWidth, srcImgHeight = srcImg.size[0], srcImg.size[1]
    srcBox, srcBoxWidth, srcBoxHeight = getBox(srcImg)
    left, right = splitYAxis(srcImg)
    leftBox, leftBoxWidth, leftBoxHeight = getBox(left)
    rightBox, rightBoxWidth, rightBoxHeight = getBox(right)
    leftCrop = left.crop(leftBox)
    rightCrop = right.crop(rightBox)
    dstImg = Image.new('L', (srcImgWidth, srcImgHeight),0)
    if type == 'pass-through':
        dstBoxWidth = srcBoxWidth
    else:
        dstBoxWidth = max(leftBoxWidth, rightBoxWidth)
    dstImg.paste(rightCrop, (0,0), mask=rightCrop)
    dstImg.paste(leftCrop, (dstBoxWidth - leftBoxWidth, 0), mask=leftCrop)
    return centerImage(dstImg)

def generateRotation(srcImg, degree, shadow=False):
    dstImg = srcImg.rotate(degree)
    if shadow:
        dstImg = Image.composite(srcImg, dstImg, mask=srcImg)
    return dstImg

def generateAddSubtract(srcImg, addImg, subImg):
    dstImg = ImageChops.add(srcImg, addImg)
    dstImg = ImageChops.subtract(dstImg, subImg)
    return dstImg

####################################
# Test Functions
####################################

def main():
    BLACK = 0
    WHITE = 255
    
    problemSet = 'Basic Problems C'
    problemName = 'Basic Problem C-08'
    problemImages = {}
    problem = Problem(problemSet, problemName)
    for figName, figObj in problem.problem.figures.items():
        fh = Image.open(figObj.visualFilename)
        problemImages[figName] = blackOut(ImageChops.invert(fh.convert('L')))
        
    figA = problemImages['A']
    figB = problemImages['C']
    figD = problemImages['D']
    figF = problemImages['F']
    figG = problemImages['G']
    ans = problemImages['8']
    
    addAC = imagesToAdd(figA, figB)
    subAC = imagesToSub(figA, figB)
    
    addDF = imagesToAdd(figD, figF)
    subDF = imagesToSub(figD, figF)
    addDF.show()
    subDF.show()
    
    dstImgDFG = generateAddSubtract(figG, addDF, subDF)
    dstImgDFG.show()
    #dstImg = generateAddSubtract(figG, addAC, subAC)
    #dstImg.show()
    #print(pixelMatch(dstImg, ans))

if __name__ == '__main__':
    main()
    