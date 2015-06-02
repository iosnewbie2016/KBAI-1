from PIL import Image

class TwoByTwo:
    LAYOUT = dict(topLeft = 'A',
                  topRight = 'B',
                  bottomLeft = 'C',
                  answers = [1, 2, 3, 4, 5, 6])
    
    def __init__(self, problem):
        self.problem = problem
        print('You created a 2x2!!!')
    
    def runAnalysis(self):
        print('Running analysis...')
        ansRow = self.getAToB(self.problem.figures[self.LAYOUT['topLeft']], self.problem.figures[self.LAYOUT['topRight']])
        ansCol = self.getAToC(self.problem.figures[self.LAYOUT['topLeft']], self.problem.figures[self.LAYOUT['bottomLeft']])
        print('ansRow: {}'.format((ansRow)))
        print('ansCol: {}'.format(str(ansCol)))
        if ansRow == ansCol:
            print('They are the same!!')
        input('Continue?')
    
    def getAToB(self, figureA, figureB):
        print('Comparing {} and {}...'.format(figureA.name,figureB.name))
        if self.isSameImage(figureA, figureB):
            print('Setting answer to image at: {}'.format(self.problem.figures[self.LAYOUT['bottomLeft']].visualFilename))
            return self.getImage(self.problem.figures[self.LAYOUT['bottomLeft']])
    
    def getAToC(self, figureA, figureC):
        print('Comparing {} and {}...'.format(figureA.name,figureC.name))
        if self.isSameImage(figureA,figureC):
            print('Setting answer to image at: {}'.format(self.problem.figures[self.LAYOUT['topRight']].visualFilename))
            return self.getImage(self.problem.figures[self.LAYOUT['topRight']])
        
    def isSameImage(self, figureA, figureB):
        if self.getImage(figureA) == self.getImage(figureB):
            return True
        else:
            return False
    
    def getImage(self, figure):
        return Image.open(figure.visualFilename)    
    
    
    
    
    
    
    
    
    
    
    
    
    def isSameShape(self, a, b):
        pass

    def isSameFill(self, a, b):
        pass
    
    def isSameSize(self, a, b):
        pass
    
    def isSameLocation(self, a, b):
        pass

    def isReflection(self):
        pass
    
    def compareSide(self, corner, adj, opp):
        if corner == adj:
            return opp
    
    def compareShape(self):
        pass
    
    def compareSize(self):
        pass
    
    def compareFill(self):
        pass
    
    def displayProblem(self, problem):
        print('Problem Details'.upper())
        print('{:-<20}'.format(''))
        print('{:>10}'.format('Type: ') + problem.problemType)
        print('{:>10}'.format('Answer: ') + str(problem.correctAnswer))
        print('{:>10}'.format('Visual: ') + str(problem.hasVisual))
        print('{:>10}'.format('Verbal: ') + str(problem.hasVerbal))
        print('\nFigures')
        print('{:-<20}'.format(''))
        for name, figure in problem.figures.items():
            #print('Name: {} | Figure: {}'.format(name, figure))
            self.displayFigure(figure)
        action = input("Continue?")
        if action == 'n':
            sys.exit(0)
    
    def displayFigure(self, figure):
        print('{:>10}'.format('Figure: ') + figure.name)
        print('{:>10}'.format('File: ') + figure.visualFilename)
        if self.problem.hasVerbal:
            for name, object in figure.objects.items():
                print('{:>20}'.format('Object Name: ') + name)
                for attribute, value in object.attributes.items():
                    print('{:>30}'.format('Attribute: ') + attribute + " = " + value)

####################
def test(figureNameA, figureNameB):
    from Test import Problem
    problemSet = 'Basic Problems B'
    problemName = 'Basic Problem B-01'
    
    problem = Problem(problemSet, problemName)
    problemSolver = TwoByTwo(problem.problem)
    figureA = problemSolver.problem.figures[figureNameA]
    figureB = problemSolver.problem.figures[figureNameB]

    imgToRed(problemSolver.getImage(figureA))
    #problemSolver.getImage(figureB)

    print(problemSolver.isSameImage(figureA, figureB))
    
def imgToRed(img):
    black = (0, 0, 0, 255)
    red = (126, 126, 0, 0)
    w, h = img.size
    for x in range(w):
        for y in range(h):
            if img.getpixel((x, y)) == black:
                img.putpixel((x, y), red)
            else:
                pass
    img.show()
    
    
if __name__ == '__main__':
    figureA = input('Figure A: ')
    figureB = input('Figure B: ')
    test(figureA, figureB)
