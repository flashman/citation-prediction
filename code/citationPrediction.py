'''
@created: Nov 6, 2013
@author: homoflashmanicus
@description: Predict citation counts of articles.
'''

import sys
from argparse import ArgumentParser
import math
import utils
import collection
import citationNetwork
import naiveBayes
import SVMLight

def loadAndLabel(network,root,start,end,nMonths=12,threshold=10,log=False):
    '''
    Load collections for each from start month to end month, inclusively.
    Add citation counts for each article obtained in in the first nMonths of it's publication.
    Merge collections into a single collection object and return.
    '''
    collections = []
    for yymm in utils.dateRange(start,end):
        #Load article data in root/<yymm>.svm 
        C = collection.Collection()
        C.load(root+yymm+'.svm')
        
        #Get inDegree of articles in the first nMonths of publication for the current collection of articles.
        inDeg = network.inDegree(start=yymm,end=utils.addMonths(yymm,nMonths))
        inDeg = network.toDict(inDeg)
        inDeg = network.filterByDate(inDeg,start=yymm,end=utils.addMonths(yymm,1))
    
        #Attach labels to articles
        #NOTE: Some articles do not appear in the citation network data.  We assume that these articles received zero citations.
        labels = []
        for l in C.labels:
            if (not log) and l in inDeg and inDeg[l] >= threshold:
                labels.append(1)
            elif log and l in inDeg and math.log(inDeg[l]) >= threshold:
                labels.append(1)
            else:
                labels.append(-1)
        C.labels = labels
        collections.append(C)

    #join and return as single collection
    C = collection.join(collections)
    return C

if __name__ == '__main__':
    '''
    The main program
    '''
    #parse inputs
    parser = ArgumentParser()
    parser.add_argument("main")
    parser.add_argument("root",help="Root directory of document feature vectors (one file per month)", default='../data/hep-th-svm/')
    parser.add_argument("citation",help="Location of citation network data.", default='../data/cit-hep-th.txt')
    parser.add_argument("-ts","--trainstart",help="Specify start date of training documets.  Eg '9501' ")
    parser.add_argument("-te","--trainend",help="Specify end date of training documets.  Eg '9601' ")
    parser.add_argument("-ps","--predictstart",help="Specify start date of prediction documets.  Eg '9501' ")
    parser.add_argument("-pe","--predictend",help="Specify end date of prediction documets.  Eg '9601' ")
    parser.add_argument("-t","--threshold",help="Citation count threshold.", type=int, default=10)
    parser.add_argument("-m","--months",help="Number of months used in tabulation of article citations.", type=int, default=12)
    parser.add_argument("-svm","--svm",help="Predict with support vector machine", action="store_true")
    parser.add_argument("-nb","--naivebayes",help="Prediict with naive bayes.", action="store_true")

    args = parser.parse_args(sys.argv)
    
    N = citationNetwork.CitationNetwork()
    N.load(args.citation)

#    print 'Preparing training data...'
#    C = loadAndLabel(N, args.root, args.trainstart, args.trainend, args.months,args.threshold)
#    print 'Preparing test data...'
#    D = loadAndLabel(N, args.root, args.predictstart, args.predictend, args.months,args.threshold)

#    if args.naivebayes:
#        print 'Training NaiveBayes Classifier...'
#        NB = naiveBayes.NaiveBayes()
#        NB.train(C.labels, C.M)
#        print 'Testing NaiveBayes Classifier...'
#        predictions = NB.test(D.M)
#        utils.report(D.labels,  predictions) 

#    if args.svm:
#        print 'Training SVM Classifier...'
#        model = SVMLight.learn(C)
#        print 'Testing SVM Classifier...'
#        predictions = [1 if p>=0 else -1 for p in SVMLight.classify(D,model)]
#        utils.report(D.labels,  predictions) 


#   print "PART 2"
    errDif = []
    err = []

    #predict citations for each month based on previous year
    for i in range(2*args.months, len(utils.YYMM)- 2*args.months-3):
        trainstart = utils.YYMM[i-args.months]
        trainend = utils.YYMM[i]
        predictstart = utils.YYMM[i+args.months+1]
        predictend = utils.YYMM[i+args.months+2]
        print "Predicting YYMM: " + predictstart

        #print 'Preparing training data...'
        trainingData = loadAndLabel(N, args.root, trainstart, trainend, args.months,args.threshold)
        #print 'Preparing test data...'
        testingData = loadAndLabel(N, args.root, predictstart, predictend, args.months,args.threshold)

        if args.naivebayes:
            #print 'Training NaiveBayes Classifier...'
            NB = naiveBayes.NaiveBayes()
            NB.train(trainingData.labels, trainingData.M)
            #print 'Testing NaiveBayes Classifier...'
            predictions = NB.test(testingData.M)
            r = utils.report(testingData.labels,  predictions)
            err.append(r[0])
            errDif.append(r[1]-r[0])

        if args.svm:
            print 'Training SVM Classifier...'
            model = SVMLight.learn(trainingData)
            print 'Testing SVM Classifier...'
            predictions = [1 if p>=0 else -1 for p in SVMLight.classify(testingData,model)]
            r = utils.report(testingData.labels,  predictions)
            err.append(r[0])
            errDif.append(r[1]-r[0])


    print err
    print errDif
    print 'AVG ERROR RATE:' + str(1.0*sum(err)/len(err))     
    print 'AVG DECREASE IN ERROR RATE:' + str(1.0*sum(errDif)/len(errDif)) 
