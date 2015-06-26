from PIL import Image
import os


        
def test():
    setName = 'Basic Problems B'
    problemName = 'Basic Problem B-04'
    imgNameA = input("Image: ")
    imgFileA = "Problems" + os.sep + setName + os.sep + problemName + os.sep + imgNameA + ".PNG"
    imgNameB = input("Image: ")
    imgFileB = "Problems" + os.sep + setName + os.sep + problemName + os.sep + imgNameB + ".PNG"
    imgA = Image.open(imgFileA)
    imgB = Image.open(imgFileB)
    
    imgDataA = imgA.getdata()
    imgDataB = imgB.getdata()
    
    w = imgA.size[0]
    h = imgA.size[1]
    
    refA = imgA.transpose(Image.FLIP_LEFT_RIGHT)
    refDataA = refA.getdata()
    
    possibleMatch = w * h
    actualMatch = 0
    actualMiss = 0
    for i in range(w*h):
        if refDataA[i] == imgDataB[i]:
            actualMatch += 1
        else:
            actualMiss += 1
            
    print('Possible: {}, Actual Match: {}, Actual Miss: {}'.format(possibleMatch, actualMatch, actualMiss))
    print('Percentage: {}'.format(actualMatch/possibleMatch*100.0))

if __name__ == "__main__":
    test()
    
    
    
    graph = {'a' : {link : 'f'},
             'b' : {link : 'e'},
             ADD : ['s']
             }
    sdf
        sdf
    
    ANS
        f
            shape:circle
            size:huge
            fill:no
        e
            shape:square
            size:medium
            fill:no
            inside:f
        s
            shape:square
            size:very small
            fill:yes
            inside:f, e
    
    
    
    
    