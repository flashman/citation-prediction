import numpy
from itertools import izip

class NaiveBayes:

    def __init__(self):
        self.trainMat = None
        self.nVocab = None

    def learn(self,trainingData,options=None):
        '''Train Naive Bayes classifier on trainingData.  trainingData is anything with label and M (matrix) properties'''
        #load data and compute basic statistics
        self.labels= trainingData.labels
        self.trainMat = trainingData.M 
        self.nVocab = self.trainMat.shape[1]
        self.nDocs = self.trainMat.shape[0]
        self.nPos = sum(1 for l in self.labels if l>0 )
        self.nNeg = sum(1 for l in self.labels if l<0 )
        self.lMajority = (1 if self.nPos>self.nNeg else -1 )
        
        #number of times each word appears in pos and neg training instances
        self.wordsPos = [ 1.0 if l>0 else 0.0  for l in self.labels] * self.trainMat
        self.wordsNeg = [ 1.0 if l<0 else 0.0 for l  in self.labels] * self.trainMat

        #total words in pos and neg training instances
        self.nWordsPos = self.wordsPos.sum()
        self.nWordsNeg = self.wordsNeg.sum()
        self.nWords = self.nWordsPos + self.nWordsNeg

        #build word probabilities for pos and neg training instances
        self.logPWordsPos = numpy.log( (1.0 + self.wordsPos ) / (self.nVocab + self.nWordsPos))
        self.logPWordsNeg = numpy.log( (1.0 + self.wordsNeg ) / (self.nVocab + self.nWordsNeg))

        print "Model trained on {0} examples".format(self.nDocs)

    def classify(self, testData, cost=(0.0,1.0,1.0,0.0),options=None,regression=False):
        '''
        Test data in testData.M  using training probabilities,
        weight prediction by cost matrix.
        '''
        testMat = testData.M
        nTestDocs,nTestVocab = testMat.shape
        #fix testMat if it doesn't include all the words 
        if nTestVocab < self.nVocab:
            testMat._shape = (nTestDocs,self.nVocab)
        else:
            testMat = testMat[:,:self.nVocab]

        #Probability that test docs are pos and neg
        pPos = numpy.log(1.0 * self.nPos / self.nDocs) + testMat * self.logPWordsPos 
        pNeg = numpy.log(1.0 * self.nNeg / self.nDocs) + testMat * self.logPWordsNeg

        predictions = []
        for pp, pn in izip(pPos,pNeg):
            #weight probibilities with cost
            pp = numpy.log(cost[2] - cost[3]) + pp 
            pn = numpy.log(cost[1] - cost[0]) + pn
            if pp>pn:
                predictions.append(1)
            elif pp<pn:
                predictions.append(-1)
            else:
                predictions.append(self.lMajority)
        return predictions
