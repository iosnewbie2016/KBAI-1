

class SemanticNet:
    #######################
    # LINKS
    #######################
    LINK = 'link'
    TRANS = 'trans'
    
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
     
    def getLinks(self, srcFig, dstFig, direction):
        possibleScore = 0
        actualScore = 0
        graph = {}
        availableObjs = list(dstFig.objects.keys())
        for srcObjName, srcObj in srcFig.objects.items():
            score = self.initScore(availableObjs)
            print('Score: {}'.format(score))
            for srcKey, srcVal in srcObj.attributes.items():
                possibleScore += self.COMPARISON_WEIGHTS[srcKey]
                print('srcKey: {}'.format(srcKey))
                self.COMPARISON_FUNCTIONS.get(srcKey)(self, srcKey, srcVal, score, **dstFig.objects)
            best = max(score, key = score.get)
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
        return 0
    
    def compareInside(self, srcKey, srcVal, score, **kwargs):
        """
        if objA.count == objB.count:
            score += 1
        else
            return 0
        """
        return 0
    
    def compareAngle(self, srcKey, srcVal, score, **kwargs):
        """
        if isReflection(imgReflect):
            score += 2
        elif objA.angle == objB.angle:
            score += 2
        elif objA.angle and objB.angle:
            score += 1
        else
            return 0
        """
        return 0
        
    
    def compareAlignment(self, srcKey, srcVal, score, **kwargs):
        """
        if objA.alignment == objB.alignment:
            score += 1
        
        """
        return 0
            
    COMPARISON_FUNCTIONS = {'shape'         : compareShape,
                            'size'          : compareSize,
                            'fill'          : compareFill,
                            'angle'         : compareAngle,
                            'alignment'     : compareAlignment,
                            'above'         : compareAbove,
                            'inside'        : compareInside
                            }
    
    #######################
    # GET TRANSFORMATIONS
    #######################
    def getTrans(self, srcFig, dstFig, graph):
        for objName, obj in graph.items():
            graph[objName][self.TRANS] = {}
            #print('{} : link = {}, trans = {}'.format(str(objName), obj[LINK], obj[TRANS]))
            for attr in srcFig.objects[objName].attributes.keys():
                self.GET_TRANS_FUNCTIONS.get(attr, self.getTransDefault)(self, srcFig.objects[objName], dstFig.objects[obj[self.LINK]], attr, graph)
    
    def getTransDefault(self, srcObj, dstObj, attr, graph):
        pass
    
    def getTransShape(self, srcObj, dstObj, attr, graph):
        if srcObj.attributes.get(attr) != dstObj.attributes.get(attr):
            graph[srcObj.name][self.TRANS][attr] = dstObj.attributes.get(attr)
            
    def getTransSize(self, srcObj, dstObj, attr, graph):
        if srcObj.attributes.get(attr) != dstObj.attributes.get(attr):
            graph[srcObj.name][self.TRANS][attr] = self.SIZE[srcObj.attributes.get(attr)] - self.SIZE[dstObj.attributes.get(attr)]
            
    def getTransFill(self, srcObj, dstObj, attr, graph):
        if srcObj.attributes.get(attr) != dstObj.attributes.get(attr):
            graph[srcObj.name][self.TRANS][attr] = dstObj.attributes.get(attr)
            
    def getTransShape(self, srcObj, dstObj, attr, graph):
        if srcObj.attributes.get(attr) != dstObj.attributes.get(attr):
            graph[srcObj.name][self.TRANS][attr] = dstObj.attributes.get(attr)
            
    GET_TRANS_FUNCTIONS = {'shape'          : getTransShape,
                           'size'           : getTransSize,
                           'fill'           : getTransFill,
                           'angle'          : getTransDefault,
                           'alignment'      : getTransDefault,
                           'above'          : getTransDefault,
                           'inside'         : getTransDefault
                           }
    
    #######################
    # APPLY TRANSFORMATIONS
    #######################
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
    
    
    APPLY_TRANS_FUNCTIONS = {'shape'        : applyTransShape,
                             'size'         : applyTransSize,
                             'fill'         : applyTransFill,
                             'angle'        : applyTransDefault,
                             'alignment'    : applyTransDefault,
                             'above'        : applyTransDefault,
                             'inside'       : applyTransDefault,
                             'action'       : applyTransDefault
                             }
    
    #######################
    # EVAL ANSWERS
    #######################
    def evalAnswers(self, ansGen, ansChoices):
        best = dict(score = 0, figure = None)
        for i in range(1,7):
            ansChoice = ansChoices.figures[str(i)]
            graph, score = self.getLinks(ansGen, ansChoice)
            if score > best.get('score'):
                best['score'] = score
                best['figure'] = i
        return best['figure']

#######################
# ANSWER CLASSES
#######################
class AnswerFigure():
    def __init__(self, fig = None):
        self.objects = {}
        self.name = 'ANS'
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
def test(figNameA, figNameB, figNameC):
    from Test import Problem
    
    problemSet = 'Basic Problems B'
    problemName = 'Basic Problem B-02'
    problem = Problem(problemSet, problemName)
    figA = problem.problem.figures[figNameA]
    figB = problem.problem.figures[figNameB]
    figC = problem.problem.figures[figNameC]

    semanticNet(figA, figB, figC, problem)

def semanticNet(figA, figB, figC, problem):
    figA = self.problem.figures[self.TOP_LEFT]
    figB = self.problem.figures[self.TOP_RIGHT]
    figC = self.problem.figures[self.BOTTOM_LEFT]
    
    sn = SemanticNet()
    graphHor, weightHor = sn.getLinks(figA, figB)
    sn.getTrans(figA, figB, graphHor)
    graphVert, weightVert = sn.getLinks(figA, figC)
    ansGen = sn.applyTrans(figB, figC, graphHor, graphVert)
    ans = sn.evalAnswers(ansGen, self.problem)
    return ans


if __name__ == '__main__':
    figureA = input('Figure A: ') or 'A'
    figureB = input('Figure B: ') or 'B'
    figureC = input('Figure C: ') or 'C'
    test(figureA, figureB, figureC)
