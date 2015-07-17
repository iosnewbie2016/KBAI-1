from PIL import Image, ImageChops, ImageFilter
from Visual import Utility

class RowOps:
    
    @staticmethod
    def add(imgA, imgB):
        return ImageChops.add(imgA, imgB)
    
    @staticmethod
    def sub(imgA, imgB):
        return ImageChops.subtract(imgA, imgB)
    
    @staticmethod
    def diff(imgA, imgB):
        return ImageChops.difference(imgA, imgB)
    
    @staticmethod
    def addBottomLeftJustified(imgA, imgB):
        return Utility.centerImage(RowOps.add(Utility.bottomLeftCornerImage(imgA), Utility.bottomLeftCornerImage(imgB)))
    
    @staticmethod
    def subBottomLeftJustified(imgA, imgB):
        return Utility.centerImage(RowOps.sub(Utility.bottomLeftCornerImage(imgA), Utility.bottomLeftCornerImage(imgB)))
    
    @staticmethod
    def diffBottomLeftJustified(imgA, imgB):
        return Utility.centerImage(RowOps.diff(Utility.bottomLeftCornerImage(imgA), Utility.bottomLeftCornerImage(imgB)))
    
    @staticmethod
    def subXOR(imgA, imgB):
        subA = RowOps.sub(imgA, imgB)
        subB = RowOps.sub(imgB, imgA)
        addAB = RowOps.add(imgA, imgB)
        return RowOps.sub(RowOps.sub(addAB, subA), subB)
    
    

def test():
    from Test import Problem
    BLACK = 0
    WHITE = 255
    
    problemSet = 'Basic Problems E'
    problemName = 'Basic Problem E-06'
    problemImages = {}
    problem = Problem(problemSet, problemName)
    for figName, figObj in problem.problem.figures.items():
        fh = Image.open(figObj.visualFilename)
        #problemImages[figName] = Utility.blackOut(ImageChops.invert(fh.convert('L')).filter(ImageFilter.GaussianBlur(3)))
        problemImages[figName] = Utility.blackOut(ImageChops.invert(fh.convert('L')))
    
    figA = problemImages['A']
    figB = problemImages['B']
    figC = problemImages['C']
    figD = problemImages['D']
    figE = problemImages['E']
    figF = problemImages['F']
    figG = problemImages['G']
    figH = problemImages['H']
    ans1 = problemImages['1']
    ans2 = problemImages['2']
    ans3 = problemImages['3']
    ans4 = problemImages['4']
    ans5 = problemImages['5']
    ans6 = problemImages['6']
    ans7 = problemImages['7']
    ans8 = problemImages['8']
    
    genImg = RowOps.diff(figD, figE)
    genImg.show()
    
    for i in range(1,9):
        print(str(i) + ': ' + str(Utility.pixelMatch(genImg, problemImages[str(i)])))


if __name__ == '__main__':
    test()