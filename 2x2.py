

class  TwoByTwo:
    CONFIG = dict(topLeft = 'A',
                  topRight = 'B',
                  botLeft = 'C',
                  answers = [1, 2, 3, 4, 5, 6])
    
    def __init__(self, problem):
        self.problem = problem
    
    def AToB(self, a, b):
        
        pass
    
    def AToC(self, a, c):
        pass
    
    def compare(self, a, adj, opp):
        if a == adj:
            return opp
        
    def isReflection(self):
        pass
    
    def compareShape(self):
        pass
    
    def compareSize(self):
        pass
    
    def compareFill(self):
        pass
    
    
    
        


def test():
    pass

if __name__ == '__main__':
    test()
