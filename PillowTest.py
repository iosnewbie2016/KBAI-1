from PIL import Image
import os

class Edge:
    COLORS = dict(black = (0, 0, 0, 255),
                  white = (255, 255, 255, 255),
                  red = (255, 0, 0, 0))
    
    def __init__(self, img):
        self.img = img
        self.edge = []
        
    def findEdge(self):
        start = self.findBlackPixel()
        next = start
        last = None
        while next:
            next, last = self.getNextPixel(next, last)
        
    def findBlackPixel(self):
        w, h = self.img.size
        for x in range(w):
            for y in range(h):
                if self.img.getpixel((x, y)) == self.COLORS.get('black'):
                    return (x, y)
                else:
                    continue
    
    def getNextPixel(self, curr, last=None):
        self.edge.append(curr)
        adjPixels = self.getAdjPixels(curr)
        end = len(adjPixels)
        for i, pixel in enumerate(adjPixels):
            if self.isLegitPixel(i, pixel, adjPixels, last):
                return pixel, curr
        return False, curr
    
    def isLegitPixel(self, i, pixel, adjPixels, last):
        if pixel != self.COLORS.get('black'):
            return False
        if adjPixels[(i - 1) % end] != self.COLORS.get('black') or adjPixels[(i + 1) % end] != self.COLORS.get('black'):
            return False
        if pixel == last:
            return False
        return True
    
    def getAdjPixels(self, xy):
        x, y = xy
        adjPixels = []
        adjPixels.append((x-1, y+1))
        adjPixels.append((x, y+1))
        adjPixels.append((x+1, y+1))
        adjPixels.append((x+1, y))
        adjPixels.append((x+1, y-1))
        adjPixels.append((x, y-1))
        adjPixels.append((x-1, y-1))
        adjPixels.append((x-1, y))
        return adjPixels
    
    def highlightEdge(self):
        for pixel in self.edge:
            self.img.putpixel(pixel, self.COLORS.get('red'))
            
    def showImage(self):
        self.img.show()
        
def test():
    setName = 'Basic Problems B'
    problemName = 'Basic Problem B-01'
    imgName = input("Image: ")
    imgFile = "Problems" + os.sep + setName + os.sep + problemName + os.sep + imgName + ".PNG"
    img = Image.open(imgFile)
    edge = Edge(img)
    edge.showImage()
    edge.findEdge()
    edge.highlightEdge()
    edge.showImage()
    print(edge.edge)

if __name__ == "__main__":
    test()