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
import pickle

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
        #NOTE: Some articles do not appear in the citation network data.  Such articles received zero citations.
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

def trainAndTest(citationNetwork,trainstart,trainend,predictstart,predictend,months,threshold,args):
    '''Train and test classifier.  Return prediction statistics'''
    if args.naivebayes: 
        classifier = naiveBayes.NaiveBayes() 
    elif args.svm:
        classifier = SVMLight.SVM() 
    else:
        print "No classifier given."
        return 

    #Preparing data...
    TRAIN = loadAndLabel(citationNetwork, args.root, trainstart, trainend, months, threshold)
    TEST = loadAndLabel(citationNetwork, args.root, predictstart, predictend, months, threshold)
    
    #classifying data...
    classifier.learn(TRAIN,options=args.options)
    predictions = classifier.classify(TEST)
    results = utils.report(TEST.labels,  predictions) 
    return results

if __name__ == '__main__':
    '''
    The main program
    '''
    #parse inputs
    parser = ArgumentParser()
    parser.add_argument("main")
    parser.add_argument("-r", "--root",help="Root directory of document feature vectors (one file per month)", default='../data/hep-th-svm/')
    parser.add_argument("-c", "--citation",help="Location of citation network data.", default='../data/cit-hep-th.txt')
    parser.add_argument("-ts","--trainstart",help="Specify start date of training documets.  Eg '9501' ")
    parser.add_argument("-te","--trainend",help="Specify end date of training documets.  Eg '9601' ")
    parser.add_argument("-tw","--trainwindow",help="Specify the size of the trainging period.  Eg 12 ", type=int, default=12)
    parser.add_argument("-ps","--predictstart",help="Specify start date of prediction documets.  Eg '9501' ")
    parser.add_argument("-pe","--predictend",help="Specify end date of prediction documets.  Eg '9601' ")
    parser.add_argument("-t","--threshold",help="Citation count threshold.", type=int, default=10)
    parser.add_argument("-m","--months",help="Number of months used in tabulation of article citations.", type=int, default=12)
    parser.add_argument("-svm","--svm",help="Predict with support vector machine", action="store_true")
    parser.add_argument("-o","--options",help="Optional parameter string for SVM classifier.  Ignored by naive bayes classifier.", type=str, default=None)
    parser.add_argument("-nb","--naivebayes",help="Prediict with naive bayes.", action="store_true")
    args = parser.parse_args(sys.argv)
    
    #Load citation network for later use
    N = citationNetwork.CitationNetwork()
    N.load(args.citation)

    #trainAndTest(N,args.trainstart,args.trainend,args.predictstart,args.predictend,args.months,args.threshold, args)

    results=dict()
    
    #predict citations for each month based on previous year
    utils.YYMM
    for yymm in utils.dateRange(args.trainstart,args.trainend):
        trainstart = yymm
        trainend = utils.addMonths(yymm,args.trainwindow)
        predictstart = utils.addMonths(yymm, args.trainwindow+args.months)
        predictend = utils.addMonths(yymm,+args.trainwindow+args.months+1) #predict on the following month's worth of data

        "TRAINING ON:"
        print trainstart
        print trainend
        "PREDICTING ON:"
        print predictstart
        print predictend
        "CITATIONS OBTAINED OVER: " + str(args.months)


        r = trainAndTest(N,trainstart, trainend, predictstart, predictend,args.months,args.threshold,args)
        results['-'.join([trainstart,trainend,predictstart,predictend])] = r

    #save results
    f = open('../results/results.pickle', 'w')
    pickle.dump(results,f)
    f.close
