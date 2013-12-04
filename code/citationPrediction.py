'''
@created: Nov 6, 2013
@author: homoflashmanicus
@description: Predict citation counts of articles.
'''

import sys
from argparse import ArgumentParser
import  datetime as dt 
import utils
import collection
import citationNetwork
import naiveBayes
import SVMLight
import pickle

def loadAndLabel(network,root,start,end,nMonths,threshold,regression):
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
        if regression:
            for l in C.labels:
                if l in inDeg:
                    labels.append(inDeg[l])
                else:
                    labels.append(0)
        else:
            for l in C.labels:
                if l in inDeg and inDeg[l] >= threshold:
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
    TRAIN = loadAndLabel(citationNetwork, args.root, trainstart, trainend, months, threshold, args.regression)
    TEST = loadAndLabel(citationNetwork, args.root, predictstart, predictend, months, threshold, args.regression)
    
    #classifying data...
    classifier.learn(TRAIN,options=args.options)
    predictions = classifier.classify(TEST,regression=args.regression)
    if args.regression:
        results = utils.report_regression(TEST.labels,predictions,epsilon=args.epsilon)
    else:
        results = utils.report(TEST.labels,  predictions) 
    return results

if __name__ == '__main__':
    '''
    The main program
    '''
    #parse inputs
    parser = ArgumentParser()
    parser.add_argument("main")
    parser.add_argument("-root", "--root",help="Root directory of document feature vectors (one file per month)", default='../data/hep-th-svm/')
    parser.add_argument("-citation", "--citation",help="Location of citation network data.", default='../data/cit-hep-th.txt')
    parser.add_argument("-ts","--trainstart",help="Specify start date of training documets.  Eg '9501' ")
    parser.add_argument("-te","--trainend",help="Specify end date of training documets.  Eg '9601' ")
    parser.add_argument("-tw","--trainwindow",help="Specify the size of the trainging period.  Eg 12 ", type=int, default=12)
    parser.add_argument("-ps","--predictstart",help="Specify start date of prediction documets.  Eg '9501' ")
    parser.add_argument("-pe","--predictend",help="Specify end date of prediction documets.  Eg '9601' ")
    parser.add_argument("-t","--threshold",help="Citation count threshold.", type=int, default=10)
    parser.add_argument("-m","--months",help="Number of months used in tabulation of article citations.", type=int, default=12)
    parser.add_argument("-svm","--svm",help="Predict with support vector machine", action="store_true")
    parser.add_argument("-r","--regression",help="Perform regression based analysis. Only valid for svm", action="store_true")
    parser.add_argument("-ep","--epsilon",help="Regression tollerence.  Only relevent  for svm regression", type=int, default=1)
    parser.add_argument("-o","--options",help="Optional parameter string for SVM classifier.  Ignored by naive bayes classifier.", type=str, default='')
    parser.add_argument("-nb","--naivebayes",help="Prediict with naive bayes.", action="store_true")
    args = parser.parse_args(sys.argv)

    if args.regression:
        args.options+=' -z r'


    #Load citation network for later use
    N = citationNetwork.CitationNetwork()
    N.load(args.citation)

    # allResults=dict()
    # x = [6,8,10,12,14,16,18,20]
    # for m in x:
    #     for w in x:
    results=[]
    
    #predict citations for each month based on previous year
    for yymm in utils.dateRange(args.trainstart,args.trainend):
        trainstart = yymm
        trainend = utils.addMonths(yymm,args.trainwindow)
        predictstart = utils.addMonths(yymm, args.trainwindow+args.months)
        predictend = utils.addMonths(yymm,+args.trainwindow+args.months+1) 
        #predict on the following month's worth of data

        print 'TRAINING RANGE: {0} -> {1}'.format(trainstart, trainend)
        print 'PREDICTION RANGE: {0} -> {1}'.format(predictstart, predictend)
        r = trainAndTest(N,trainstart, trainend, predictstart, predictend,args.months,args.threshold,args)
        results.append( r )

    #save results
    datestring =  str(dt.datetime.now()).replace(' ','_')
    method = 'regression' if args.regression else 'binary'
    filename = method + '.{0}-{1}-{2}-{3}.{4}'.format(args.months,args.trainwindow,args.trainstart,args.trainend, datestring)
    f = open('../results/'+ filename+'.pickle', 'w')
    data = {'results':results,'metadata':args }
    pickle.dump(data,f)
    f.close
