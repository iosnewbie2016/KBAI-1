from PIL import Image, ImageDraw
from Test import Problem

def floodFind(image, value):
    """Uses flood fill to detct regions of a color"""
    image = image.copy()
    regions = 0
    try:
        while True:
            i = list(image.getdata()).index(value)
            regions += 1
            ImageDraw.floodfill(Image, self.flat_to_xy(i, image.size[0]), regions)
    except ValueError:
            pass
        
    res = []
    for i in xrange(1, regions + 1):
        foundimage = image.point(lambda a: 255 if a == i else 0)
        bb = foundimage.getbox()
        if bb == None:
            continue
        start = (bb[0], bb[1])
        size = (bb[2] - bb[0], bb[3] - bb[1])
        foundimage = foundimage.crop(bb)
        res.append((start, size, list(foundimage.getdata())))
    return res


def main():
    BLACK = (0,0,0,255)
    WHITE = (255,255,255,255)
    
    figNameA = 'A'
    figNameB = 'B'
    figNameC = 'C'
    problemSet = 'Basic Problems C'
    problemName = 'Basic Problem C-01'
    problemImages = {}
    problem = Problem(problemSet, problemName)
    for figName, figObj in problem.problem.figures.items():
        problemImages[figName] = Image.open(figObj.visualFilename)
        
    figA = problemImages['A']
    i = list(figA.getdata()).index((0,0,0,255))
    print(i)

if __name__ == '__main__':
    main()
    