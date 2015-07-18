from Affine import Generate, Compare
from Utility import Utility
from PIL import Image, ImageChops, ImageFilter
import time

class  ThreeByThree:
    ANS_THRESHOLD = .90
    
    def __init__(self, problem):
        self.problem = problem
        self.problemImages = {}
        for figName, figObj in problem.figures.items():
            fh = Image.open(figObj.visualFilename)
            self.problemImages[figName] = Utility.blackOut(ImageChops.invert(fh.convert('L')))
            #self.problemImages[figName] = Utility.blackOut(ImageChops.invert(fh.convert('L')).filter(ImageFilter.GaussianBlur(3)))
        self.a_c = Compare('A_C', self.problemImages['A'], self.problemImages['C'], 'G')
        self.b_c = Compare('B_C', self.problemImages['B'], self.problemImages['C'], 'H')
        self.d_f = Compare('D_F', self.problemImages['D'], self.problemImages['F'], 'G')
        self.e_f = Compare('E_F', self.problemImages['E'], self.problemImages['F'], 'H')
            
    def solve(self):
        self.compareImages(self.a_c)
        self.compareImages(self.d_f)
        self.compareImages(self.b_c)
        self.compareImages(self.e_f)
        
        bestTransformCol1 = self.compareTransformsSameCols(self.a_c, self.d_f)
        bestTransformCol2 = self.compareTransformsSameCols(self.b_c, self.e_f)
        bestTransform = self.compareTransformsDiffCols(bestTransformCol1, bestTransformCol2)
        
        genImg = self.generateImage(bestTransform)
        #genImg.show()
        score, ansNum = self.evalAnswers(genImg)
        #print('Score: {}'.format(score))
        if score > self.ANS_THRESHOLD:
            return ansNum
        else:
            return -1

    def compareImages(self, compareObj):
        compareObj.same(compareObj.srcFig, compareObj.dstFig)
        compareObj.reflectionXAxis(compareObj.srcFig, compareObj.dstFig)
        compareObj.reflectionYAxis(compareObj.srcFig, compareObj.dstFig)
        compareObj.translation(compareObj.srcFig, compareObj.dstFig)
        compareObj.crossXAxis(compareObj.srcFig, compareObj.dstFig)
        compareObj.rotation(compareObj.srcFig, compareObj.dstFig)
        compareObj.imagesToAdd(compareObj.srcFig, compareObj.dstFig)
        compareObj.imagesToSub(compareObj.srcFig, compareObj.dstFig)
        
    def compareTransformsSameCols(self, objA, objB):
        addScore = Utility.pixelMatch(objA.add, objB.add)
        subScore = Utility.pixelMatch(objA.sub, objB.sub)
        addSubScore = (addScore + subScore)/2
        if addSubScore > objA.ADD_SUB_THRESHOLD:
            addSubScore += objA.WEIGHTS['addSub']
        if addSubScore > objA.bestScore and addSubScore > objB.bestScore:
            objA.bestScore, objB.bestScore = addSubScore, addSubScore
            objA.bestTransform, objB.bestTransform = 'add_sub', 'add_sub'
            return objA
        elif objA.bestScore > objB.bestScore:
            return objA
        else:
            return objB
        
    def compareTransformsDiffCols(self, objA, objB):
        if objA.bestScore > objB.bestScore:
            return objA
        else:
            return objB
        
    def generateImage(self, obj):
        srcImg = self.problemImages[obj.ansCol]
        if obj.bestTransform == 'identity':
            return srcImg
        elif obj.bestTransform == 'reflect_x':
            return Generate.reflectionXAxis(srcImg)
        elif obj.bestTransform == 'reflect_y':
            return Generate.reflectionYAxis(srcImg)
        elif obj.bestTransform == 'translate':
            return Generate.translation(srcImg, obj.transWidth, obj.transHeight)
        elif obj.bestTransform == 'cross_x':
            return Generate.crossX(srcImg, obj.crossXType)
        elif obj.bestTransform == 'cross_y':
            return Generate.crossY(srcImg, obj.crossYType)
        elif obj.bestTransform == 'rotate':
            return Generate.rotation(srcImg, obj.rotateDegree, obj.rotateShadow)
        elif obj.bestTransform == 'add_sub':
            return Generate.addSubtract(srcImg, obj.add, obj.sub)
        else:
            print('Why no transform?')
            return None
        
    def evalAnswers(self, genImg):
        bestScore = 0
        bestNum = 0
        for i in range(1,9):
            score = Utility.pixelMatch(genImg, self.problemImages[str(i)])
            if score > bestScore:
                bestScore = score
                bestNum = i
        return bestScore, bestNum
    
def test():
    from Test import Problem
    
    startTime = time.time()
    
    problemSet = 'Basic Problems C'
    problemName = 'Basic Problem C-12'
    problemImages = {}
    problem = Problem(problemSet, problemName)
    threeByThree = ThreeByThree(problem.problem)
    ans = threeByThree.solve()
    print('A -> C: Best Score: {}, Best Transform: {}'.format(threeByThree.a_c.bestScore, threeByThree.a_c.bestTransform))
    print('D -> F: Best Score: {}, Best Transform: {}'.format(threeByThree.d_f.bestScore, threeByThree.d_f.bestTransform))
    
    endTime = time.time()
    print('Test Time: {}'.format(endTime - startTime))
    print('Answer: {}'.format(ans))
    

if __name__ == '__main__':
    test()