from SemanticNet import SemanticNet
from SemanticNet import Links
from SemanticNet import Generate
from SemanticNet import Test
from SemanticNet import AnswerFigure
from SemanticNet import AnswerObject

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
    
    def runAnalysis(self):
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
    
####################
def test():
    pass
    
if __name__ == '__main__':
    test()
