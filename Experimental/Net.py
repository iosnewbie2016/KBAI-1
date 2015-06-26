from Neuron import Neuron

class Net:
    
    def __init__(self, topo):
        self.layers = []
        numLayers = len(topo)
        for layerNum in range(numLayers):
            layer = []
            for neuronNum in range(topo[layerNum] + 1): # +1 for bias layer
                layer.append(Neuron())
            self.layers.append(layer)
    
    def feedForward(self, inputVals):
        pass
    
    def backProp(self, targetVals):
        pass
    
    def getResults(self, resultVals):
        pass
    
def main():
    topo = [3, 2, 1]
    myNet = Net(topo)
    for each in myNet.layers:
        print(each)
    
    """
    inputVals = []
    myNet.feedForward(inputVals)
    
    targetVals = []
    myNet.backProp(targetVals)
    
    resultVals = []
    myNet.getResults(resultVals)
    """
if __name__ == '__main__':
    main()
    
