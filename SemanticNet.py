"""
01. Create semantic net between A and B
    a. Compare the objects of the second figure against one of the first
        i. Use a ranking system and generator function to ouput any objects that meet the criteria
    b. Create dict of what maps to what
    c. Using the dict, create a transform dict using well-known transformations
    d. Store for use in generating the next figure
02. Create semantic net between A and C
    a. Compare objects of figures in same way, except using vertical for reflections and rotations
    b. Once the dict mapping is created, apply the transform dict from part 01 to create image
    c. Store generated image for testing
03. Test image against possible answers
    a. Iterate through all answer figures and compare how well they match up
    b. If the match up score is perfect, or close, use that answer
    c. Keep the max answer after each iteration
04. Return answer

CONSTANTS
    SIZE = {'very small' = 0,
            'small' = 1,
            'medium' = 2,
            'large' = 3,
            'very large' = 4,
            'huge' = 5
            }
DATA STRUCTURES
    2X2
    3X3
    Semantic net
    Transformation
FUNCTIONS
    getObjectCount
    applyTransform
    evalAnswers
    isSameShape
    isSameSize
    isSameFill
    isSameAlignment
    isSameInside
    isReflection
    isRotation
    doTransformation(keyword)
    doAction(enum) # Create an action enum list that can be iterated by priority
        i.e     1 -> Shape
                2 -> Size
                3 -> Fill
                4 -> Reflection(Angle)
                5 -> Rotation(Angle)
                6 -> Inside
                7 -> Alignment #Need to separate into 2 i.e. top-left = top AND left
                8 -> Above
    
"""

COMPARISON_WEIGHTS = {'shape'        : 4,
                      'size'         : 4,
                      'reflection'   : 2,
                      'rotation'     : 1,
                      'fill'         : 2,
                      'alignment'    : 1,
                      'above'        : 1,
                      'inside'       : 1}

def semanticNet(srcFig, dstFig):
    availableObjs = dstFig.objects
    graph = {}
    for srcObjName, srcObj in srcFig.objects:
        score = initScore(availableObjs)
        for srcKey, srcVal in srcObj.attributes:
            #COMPARISON_FUNCTIONS.get(srcKey)(score, srcVal, **availableObjs)
            compare(srcKey, srcVal, score, **availableObjs)
        # best = max(score, key = score.get)
        # availableObjs.del(best)
            
def initScore(objs):
    score = {}
    for name in objs:
        score[name] = 0
    return score

def compare(srcKey, srcVal, score, **kwargs):
    for dstName, dstObj in kwargs:
        if dstObj.attributes.get(srcKey, False) == srcVal:
            score[dstName] += COMPARISON_WEIGHTS[dstName]
        
def compareShape(score, srcVal, **kwargs):
    for dstName, dstObj in kwargs:
        if dstObj.attributes.get('shape', False) == srcVal:
            score[dstName] += COMPARISON_WEIGHTS[dstName]
        
def compareSize(score, srcVal, **kwargs):
    pass

def compareFill(score, srcVal, **kwargs):
    pass
    
COMPARISON_FUNCTIONS = {'shape' : compareShape,
                        'size'  : compareSize,
                        'fill'  : compareFill}

def main():
    compare('shape')

if __name__ == '__main__':
    main()