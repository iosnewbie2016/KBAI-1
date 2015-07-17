from SemanticNet import SemanticNet
from SemanticNet import Links
from SemanticNet import Generate
from SemanticNet import Test
from SemanticNet import AnswerFigure
from SemanticNet import AnswerObject
from Visual import Utility, Generate, Compare
from PIL import Image, ImageChops, ImageFilter

class TwoByTwo:
    TOP_LEFT = 'A'
    TOP_RIGHT = 'B'
    BOTTOM_LEFT = 'C'
    ANSWERS = [1, 2, 3, 4, 5, 6]
    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'
    DIAGONAL = 'diagonal'
    
    def __init__(self, problem):
        self.problem = problem
        #print('You created a 2x2!!!')
    
    def solve(self):
        ans = self.AB_CD()
        return ans

    def AB_CD(self):
        figA = self.problem.figures[self.TOP_LEFT]
        figB = self.problem.figures[self.TOP_RIGHT]
        figC = self.problem.figures[self.BOTTOM_LEFT]
        
        hor = Links(figA, figB, self.HORIZONTAL)
        horGraph, horWeight = hor.getLinks(figA, figB)
        horGraph = hor.getTrans(figA, figB, horGraph)
        
        vert = Links(figA, figC, self.VERTICAL)
        vertGraph, vertWeight = vert.getLinks(figA, figC)
        
        gen = Generate(figB, figC, self.HORIZONTAL)
        genAns = gen.applyTrans(figB, figC, horGraph, vertGraph)
        
        test = Test(self.HORIZONTAL)
        if genAns.type == 'verbal':
            testAns = test.evalAnswers(genAns, self.problem)
        elif genAns.type == 'visual':
            testAns = test.evalAnswersVisual(genAns, self.problem)
        else:
            testAns = -1

        return testAns
    
    def AC_BD(self, figureA, figureC):
        pass
    
class TwoByTwoVisual:
    ANS_THRESHOLD = .90
    
    def __init__(self, problem):
        self.problem = problem
        self.problemImages = {}
        for figName, figObj in problem.figures.items():
            fh = Image.open(figObj.visualFilename)
            self.problemImages[figName] = Utility.blackOut(ImageChops.invert(fh.convert('L')))
            #self.problemImages[figName] = Utility.blackOut(ImageChops.invert(fh.convert('L')).filter(ImageFilter.GaussianBlur(3)))
        self.a_b = Compare('A_B', self.problemImages['A'], self.problemImages['B'], 'C')
        self.a_c = Compare('A_C', self.problemImages['A'], self.problemImages['C'], 'B')
            
    def solve(self):
        self.compareImages(self.a_b)
        self.compareImages(self.a_c)
        
        bestTransform = self.compareTransforms(self.a_b, self.a_c)
        #bestTransform = self.compareTransformsDiffCols(self.a_b, self.a_c)
        
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
        
    def compareTransforms(self, objA, objB):
        a_b_addSub = Generate.addSubtract(self.problemImages[objA.ansCol], objA.add, objA.sub)
        a_c_addSub = Generate.addSubtract(self.problemImages[objB.ansCol], objB.add, objB.sub)
        a_c_addSub, a_b_addSub = Generate.addSubtractDiff(a_c_addSub, a_b_addSub)
        
        addSubScore = Utility.pixelMatch(a_b_addSub, a_c_addSub)
        print('addSubScore: {}'.format(addSubScore))
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
        for i in range(1,7):
            score = Utility.pixelMatch(genImg, self.problemImages[str(i)])
            if score > bestScore:
                bestScore = score
                bestNum = i
        return bestScore, bestNum
    
####################
def test():
    from Test import Problem
    
    problemSet = 'Basic Problems B'
    problemName = 'Basic Problem B-11'
    problemImages = {}
    problem = Problem(problemSet, problemName)
    twoByTwo = TwoByTwoVisual(problem.problem)
    ans = twoByTwo.solve()
    print('A -> C: Best Score: {}, Best Transform: {}'.format(twoByTwo.a_c.bestScore, twoByTwo.a_c.bestTransform))
    print('A -> B: Best Score: {}, Best Transform: {}'.format(twoByTwo.a_b.bestScore, twoByTwo.a_b.bestTransform))
    print('Answer: {}'.format(ans))
    

if __name__ == '__main__':
    test()