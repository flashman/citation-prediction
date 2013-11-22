import numpy
from itertools import izip

class NaiveBayes:

    def __init__(self):
        self.trainMat = None
        self.nVocab = None

    def train(self,labels,matrix):
        '''Train Naive Bayes classifier on data in fileLocation'''
        #load data and compute basic statistics
        self.labels= labels
        self.trainMat = matrix 
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

    def test(self, testMat, cost=(0.0,1.0,1.0,0.0)):
        '''
        Test data in fileLocation using training probabilities,
        weight prediction by cost matrix.
        '''
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

    def report(self,labels,predictions):
        errors=0
        falsePos=0
        falseNeg=0
        truePos=0
        trueNeg=0
        for p,l in izip(predictions,labels):
            if p!=l:
                errors +=1
                if l==1:
                    falseNeg+=1
                else:
                    falsePos+=1
            else:
                if l==1:
                    truePos+=1
                else:
                    trueNeg+=1
        print "Document trained on: " + str(self.nDocs)
        print "Documents classified: " + str(len(labels))
        print "True Positives: " + str(truePos) 
        print "True Negatives: " + str(trueNeg) 
        print "False Positives: " + str(falsePos)
        print "False Negatives: " + str(falseNeg)
        print "Errors: " + str(errors)
        print "Error rate: " + str(1.0*errors/len(labels))
