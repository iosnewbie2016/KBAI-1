from PIL import Image
import hashlib

class SemanticNet:
    #######################
    # LINKS
    #######################
    LINK = 'link'
    TRANS = 'trans'
    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'
    DIAGONAL = 'diagonal'
    ACTION = 'action'
    REFLECT = 'reflect'
    ADD = 'add'
    DELETE = 'del'
    SAME = 'same'
    
    COMPARISON_WEIGHTS = {'shape'       : 4,
                          'size'        : 4,
                          'fill'        : 2,
                          'reflection'  : 2,
                          'angle'       : 2,
                          'rotation'    : 1,
                          'alignment'   : 1,
                          'above'       : 1,
                          'inside'      : 1
                          }
    
    SIZE = {'very small'    : 0,
            'small'         : 1,
            'medium'        : 2,
            'large'         : 3,
            'very large'    : 4,
            'huge'          : 5
            }
    
    SIZE_INVERSE = {0 : 'very small',
                    1 : 'small',
                    2 : 'medium',
                    3 : 'large',
                    4 : 'very large',
                    5 : 'huge'
                    }
    
    def getImage(self, fig):
        im = Image.open(fig.visualFilename)
        return im

    def isReflection(self):
        srcImg = self.getImage(self.srcFig)
        refImg = self.reflectImage(srcImg, self.direction)
        dstImg = self.getImage(self.dstFig)
        if self.isSameImage(refImg, dstImg):
            dstImg.close()
            refImg.close()
            srcImg.close()
            return True
        else:
            dstImg.close()
            refImg.close()
            srcImg.close()
            return False
        """
        refImgHash = self.hashImage(refImg)
        dstImgHash = self.hashImage(dstImg)
        if refImgHash == dstImgHash:
            dstImg.close()
            refImg.close()
            return True
        dstImg.close()
        refImg.close()
        return False
        """
    
    def reflectImage(self, img, direction):
        if direction == self.HORIZONTAL:
            refImg = img.transpose(Image.FLIP_LEFT_RIGHT)
            return refImg
        elif direction == self.VERTICAL:
            refImg = img.transpose(Image.FLIP_TOP_BOTTOM)
            return refImg
        else:
            refImg = img
            return refImg
    
    def isSameImage(self, srcImg, dstImg):
        srcImgData = srcImg.getdata()
        dstImgData = dstImg.getdata()
        w = srcImg.size[0]
        h = srcImg.size[1]
        possibleMatch = w * h
        actualMatch = 0
        actualMiss = 0
        for i in range(w*h):
            if srcImgData[i] == dstImgData[i]:
                actualMatch += 1
            else:
                actualMiss += 1
        #print('Possible: {}, Actual Match: {}, Actual Miss: {}'.format(possibleMatch, actualMatch, actualMiss))
        #print('Percentage: {}'.format(actualMatch/possibleMatch*100.0))
        if actualMatch/possibleMatch*100.0 > 95.0:
            #print('Match!')
            return True
        else:
            return False
        """
        if self.hashImage(srcImg) == self.hashImage(dstImg):
            return True
        else:
            return False
        """
    
    def hashImage(self, img):
        return hashlib.md5(img.tobytes()).hexdigest()
    
    def getObjectCount(self, srcFig, dstFig):
        srcObjCount = len(srcFig.objects)
        dstObjCount = len(dstFig.objects)
        return srcObjCount, dstObjCount
    
#######################
# LINKS
#######################   
class Links(SemanticNet):
    def __init__(self, srcFig, dstFig, direction):
        self.direction = direction
        self.srcFig = srcFig
        self.dstFig = dstFig
    
    def getLinks(self, srcFig, dstFig):
        possibleScore = 0
        actualScore = 0
        graph = {}
        availableObjs = list(dstFig.objects.keys())
        for srcObjName, srcObj in srcFig.objects.items():
            score = self.initScore(availableObjs)
            #if dstFig.objects.get('p', None) != None:
                #print('p: {}'.format(dstFig.objects.get('p', None).attributes))
            for srcKey, srcVal in srcObj.attributes.items():
                possibleScore += self.COMPARISON_WEIGHTS[srcKey]
                self.COMPARISON_FUNCTIONS.get(srcKey)(self, srcKey, srcVal, score, **dstFig.objects)
            #print('Score: {}'.format(score))
            best = self.getBestScore(score, srcObj, **dstFig.objects)
            #best = max(score, key = score.get)
            actualScore += score.get(best)
            graph[srcObjName] = {}
            graph[srcObjName][self.LINK] = best
        weight = actualScore/possibleScore*100.0
        #TODO: Check availableObjs for DEL, ADD, and NO DUPS
        return graph, weight
       
    def initScore(self, objs):
        score = {}
        for name in objs:
            score[name] = 0
        return score
    
    def getBestScore(self, score, srcObj, **dstObjs):
        OBJ = 'obj'
        SCORE = 'score'
        best = dict(score = 0, obj = [])
        for dstObjName, obj in dstObjs.items():
            #print('Score: {}, Best Score: {}'.format(score[objName], best['score']))
            if score[dstObjName] > best[SCORE]:
                best[SCORE] = score[dstObjName]
                best[OBJ] = [dstObjName]
            elif score[dstObjName] == best[SCORE]:
                best[OBJ].append(dstObjName)
            else:
                continue
        if len(best[OBJ]) > 1:
            srcObjLen = len(srcObj.attributes)
            newBest = []
            for dstObjName in best[OBJ]:
                if len(dstObjs[dstObjName].attributes) == srcObjLen:
                    newBest.append(dstObjName)
            best[OBJ] = newBest
        return best[OBJ][0]
    
    def compareDefault(self, srcKey, srcVal, score, **kwargs):
        return 0
    
    def compareObjectCount(self):
        """
        if srcObj.count > 0 and dstObj.count > 0:
            continue
        elif srcObj.count > 0:
            action = 'DELETE'
        elif dstObj.count > 0:
            action = 'ADD'
        else
            continue
        """
        pass
    
    def compareShape(self, srcKey, srcVal, score, **kwargs):
        for dstName, dstObj in kwargs.items():
            if dstObj.attributes.get(srcKey, False) == srcVal:
                #print('Key: {}'.format(srcKey))
                score[dstName] += self.COMPARISON_WEIGHTS.get(srcKey, 0)
                
    def compareSize(self, srcKey, srcVal, score, **kwargs):
        for dstName, dstObj in kwargs.items():
            if dstObj.attributes.get(srcKey, False) == srcVal:
                #print('Key: {}'.format(srcKey))
                score[dstName] += self.COMPARISON_WEIGHTS.get(srcKey, 0)
                
    def compareFill(self, srcKey, srcVal, score, **kwargs):
        for dstName, dstObj in kwargs.items():
            if dstObj.attributes.get(srcKey, False) == srcVal:
                #print('Key: {}'.format(srcKey))
                score[dstName] += self.COMPARISON_WEIGHTS.get(srcKey, 0)
                
    def compareAbove(self, srcKey, srcVal, score, **kwargs):
        for dstName, dstObj in kwargs.items():
            if len(dstObj.attributes.get(srcKey, [])) == len(srcVal):
                #print('Key: {}'.format(srcKey))
                score[dstName] += self.COMPARISON_WEIGHTS.get(srcKey, 0)
    
    def compareInside(self, srcKey, srcVal, score, **kwargs):
        """
        if objA.count == objB.count:
            score += 1
        else
            return 0
        """
        return 0
    
    def compareAngle(self, srcKey, srcVal, score, **kwargs):
        if self.srcFig != None:
            for dstName, dstObj in kwargs.items():
                if self.isReflection():
                    score[dstName] += self.COMPARISON_WEIGHTS.get(srcKey, 0)
                elif dstObj.attributes.get(srcKey, False) == srcVal:
                    score[dstName] += self.COMPARISON_WEIGHTS.get(srcKey, 0)
        else:
            for dstName, dstObj in kwargs.items():
                if dstObj.attributes.get(srcKey, False) == srcVal:
                    score[dstName] += self.COMPARISON_WEIGHTS.get(srcKey)
    
    def compareAlignment(self, srcKey, srcVal, score, **kwargs):
        for dstName, dstObj in kwargs.items():
            if dstObj.attributes.get(srcKey, False) == srcVal:
                #print('Key: {}'.format(srcKey))
                score[dstName] += self.COMPARISON_WEIGHTS.get(srcKey, 0)
        """
        if objA.alignment == objB.alignment:
            score += 1
        
        """
        pass
            
    COMPARISON_FUNCTIONS = {'shape'         : compareShape,
                            'size'          : compareSize,
                            'fill'          : compareFill,
                            'angle'         : compareAngle,
                            'alignment'     : compareAlignment,
                            'above'         : compareAbove,
                            'inside'        : compareInside
                            }
    
    #######################
    #----------------------------------------------------- # GET TRANSFORMATIONS
    #######################
    def getTrans(self, srcFig, dstFig, graph):
        for objName, obj in graph.items():
            if graph[objName].get(self.TRANS, False) == False:
                graph[objName][self.TRANS] = {}
                #print('{} : link = {}, trans = {}'.format(str(objName), obj[LINK], obj[TRANS]))
                for attr in srcFig.objects[objName].attributes.keys():
                    self.GET_TRANS_FUNCTIONS.get(attr, self.getTransDefault)(self, srcFig.objects[objName], dstFig.objects[obj[self.LINK]], attr, graph)
        return graph
    
    def getTransDefault(self, srcObj, dstObj, attr, graph):
        pass
    
    def getTransShape(self, srcObj, dstObj, attr, graph):
        if srcObj.attributes.get(attr) != dstObj.attributes.get(attr):
            graph[srcObj.name][self.TRANS][attr] = dstObj.attributes.get(attr)
            
    def getTransSize(self, srcObj, dstObj, attr, graph):
        if srcObj.attributes.get(attr) != dstObj.attributes.get(attr):
            graph[srcObj.name][self.TRANS][attr] = self.SIZE[srcObj.attributes.get(attr)] - self.SIZE[dstObj.attributes.get(attr)]
            
    def getTransFill(self, srcObj, dstObj, attr, graph):
        if srcObj.attributes.get(attr, 0) != dstObj.attributes.get(attr):
            graph[srcObj.name][self.TRANS][attr] = dstObj.attributes.get(attr)
            
    def getTransShape(self, srcObj, dstObj, attr, graph):
        if srcObj.attributes.get(attr) != dstObj.attributes.get(attr):
            graph[srcObj.name][self.TRANS][attr] = dstObj.attributes.get(attr)
        
    def getTransAngle(self, srcObj, dstObj, attr, graph):
        #print('Getting Angle!')
        if srcObj.attributes.get(attr) != dstObj.attributes.get(attr):
            if self.isReflection():
                graph[srcObj.name][self.TRANS][self.ACTION] = self.REFLECT
            #graph[srcObj.name][self.TRANS][attr] = dstObj.attributes.get(attr)  
            
    def getTransAlignment(self, srcObj, dstObj, attr, graph):
        srcAlignment = srcObj.attributes.get(attr)
        dstAlignment = dstObj.attributes.get(attr)
        if srcAlignment != dstAlignment:
            srcRow, srcCol = srcAlignment.split('-')
            dstRow, dstCol = dstAlignment.split('-')
            if srcRow == dstRow:
                transRow = self.SAME
            else:
                transRow = dstRow
            if srcCol == dstCol:
                transCol = self.SAME
            else:
                transCol = dstCol
            transAction = '-'.join([transRow, transCol])
            graph[srcObj.name][self.TRANS][attr] = transAction
            
    GET_TRANS_FUNCTIONS = {'shape'          : getTransShape,
                           'size'           : getTransSize,
                           'fill'           : getTransFill,
                           'angle'          : getTransAngle,
                           'alignment'      : getTransAlignment,
                           'above'          : getTransDefault,
                           'inside'         : getTransDefault
                           }

#######################
# APPLY TRANSFORMATIONS
#######################
class Generate(SemanticNet):
    def __init__(self, srcFig, dstFig, direction):
        self.direction = direction
        self.srcFig = srcFig
        self.dstFig = dstFig

    def applyTrans(self, srcFig, dstFig, srcGraph, dstGraph):
        ansFig = AnswerFigure(dstFig)
        for baseObjName in srcGraph.keys():
            srcObj = srcFig.objects[srcGraph[baseObjName][self.LINK]] 
            dstObj = dstFig.objects[dstGraph[baseObjName][self.LINK]]
            for transName, transAction in srcGraph[baseObjName][self.TRANS].items():
                #print('Trans: {}, Action: {}'.format(transName, transAction))
                self.APPLY_TRANS_FUNCTIONS[transName](self, transName, transAction, ansFig, dstObj.name)
        #print(ansFig)
        return ansFig
            
    
    def applyTransDefault(self, transName, transAction, ansFig, objName):
        pass
    
    def applyTransShape(self, transName, transAction, ansFig, objName):
        ansFig.objects[objName].attributes[transName] = transAction
        
    def applyTransSize(self, transName, transAction, ansFig, objName):
        #use SIZE table
        curSize = self.SIZE[ansFig.objects[objName].attributes[transName]]
        newSize = curSize - transAction
        ansFig.objects[objName].attributes[transName] = self.SIZE_INVERSE[newSize]
        
    def applyTransFill(self, transName, transAction, ansFig, objName):
        ansFig.objects[objName].attributes[transName] = transAction
        
    def applyTransAlignment(self, transName, transAction, ansFig, objName):
        curAlignment = ansFig.objects[objName].attributes[transName]
        curRow, curCol = curAlignment.split('-')
        transRow, transCol = transAction.split('-')
        if transRow != self.SAME:
            newRow = transRow
        else:
            newRow = curRow
        if transCol != self.SAME:
            newCol = transCol
        else:
            newCol = curCol
        newAlignment = '-'.join([newRow, newCol])
        ansFig.objects[objName].attributes[transName] = newAlignment
        

    
    def applyTransAction(self, transName, transAction, ansFig, objName):
        if transAction == self.REFLECT:
            ansFig.type = 'visual'
            ansFig.img = self.reflectImage(self.getImage(ansFig.fig), self.direction)
            return
        
    
    
    APPLY_TRANS_FUNCTIONS = {'shape'        : applyTransShape,
                             'size'         : applyTransSize,
                             'fill'         : applyTransFill,
                             'angle'        : applyTransDefault,
                             'alignment'    : applyTransAlignment,
                             'above'        : applyTransDefault,
                             'inside'       : applyTransDefault,
                             'action'       : applyTransAction
                             }

#######################
# EVAL ANSWERS
#######################    
class Test(Links):
    def __init__(self, direction):
        self.direction = direction
        self.srcFig = None

    def evalAnswers(self, ansGen, ansChoices):
        best = dict(score = 0, figure = None)
        for i in range(1,7):
            ansChoice = ansChoices.figures[str(i)]
            graph, score = self.getLinks(ansGen, ansChoice)
            if score > best.get('score'):
                best['score'] = score
                best['figure'] = i
        return best['figure']
    
    def evalAnswersVisual(self, ansGen, ansChoices):
        for i in range(1,7):
            ansChoice = ansChoices.figures[str(i)]
            if self.isSameImage(ansGen.img, self.getImage(ansChoice)):
                return i
            else:
                continue
        return -1

    def compareAngle(self, srcKey, srcVal, score, **kwargs):
        for dstName, dstObj in kwargs.items():
            if dstObj.attributes.get(srcKey, False) == srcVal:
                #print('Key: {}'.format(srcKey))
                score[dstName] += self.COMPARISON_WEIGHTS.get(srcKey, 0)
            else:
                return 0

#######################
# ANSWER CLASSES
#######################
class AnswerFigure():
    def __init__(self, fig = None):
        self.objects = {}
        self.type = 'verbal'
        self.name = 'ANS'
        self.fig = fig
        self.img = None
        if fig != None: 
            self.createBaseObjects(fig)
        
    def createBaseObjects(self, fig):
        for objName, obj in fig.objects.items():
            self.objects[objName] = AnswerObject(objName, obj)
    
class AnswerObject():
    def __init__(self, name, obj):
        self.attributes = {}
        self.name = name
        self.createBaseAttributes(obj)
    
    def createBaseAttributes(self, obj):
        for k, v in obj.attributes.items():
            self.attributes[k] = v
            
#######################
# TESTING
#######################
HORIZONTAL = 'horizontal'
VERTICAL = 'vertical'
DIAGONAL = 'diagonal'

def test(figNameA, figNameB, figNameC):
    from Test import Problem
    
    problemSet = 'Basic Problems B'
    problemName = 'Basic Problem B-11'
    problem = Problem(problemSet, problemName)
    figA = problem.problem.figures[figNameA]
    figB = problem.problem.figures[figNameB]
    figC = problem.problem.figures[figNameC]

    semanticNet(figA, figB, figC, problem)

def semanticNet(figA, figB, figC, problem):
    hor = Links(figA, figB, HORIZONTAL)
    horGraph, horWeight = hor.getLinks(figA, figB)
    horGraph = hor.getTrans(figA, figB, horGraph)
    
    vert = Links(figA, figC, VERTICAL)
    vertGraph, vertWeight = vert.getLinks(figA, figC)

    gen = Generate(figB, figC, HORIZONTAL)
    genAns = gen.applyTrans(figB, figC, horGraph, vertGraph)
    
    test = Test(HORIZONTAL)
    #print('Type: {}'.format(genAns.type))
    if genAns.type == 'verbal':
        testAns = test.evalAnswers(genAns, problem.problem)
    elif genAns.type == 'visual':
        testAns = test.evalAnswersVisual(genAns, problem.problem)
    else:
        testAns = -1

    print('horGraph: {}'.format(str(horGraph)))
    print('vertGraph: {}'.format(str(vertGraph)))
    
    print('\nAnswer: {}'.format(testAns))


if __name__ == '__main__':
    figureA = 'A' #input('Figure A: ') or 'A'
    figureB = 'B' #input('Figure B: ') or 'B'
    figureC = 'C' #input('Figure C: ') or 'C'
    test(figureA, figureB, figureC)
