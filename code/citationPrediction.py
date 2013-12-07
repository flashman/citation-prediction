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

def loadAndLabel(network,root,start,end,nMonths,citationThreshold=None,regression=False):
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
        deg =  [inDeg[l] if l in inDeg else 0 for l in C.labels]
        if citationThreshold==None and not regression:
            citationThreshold = max(sorted(deg)[C.nDocs/2],1)
            print 'Computed CitationThreshold: ' + str(citationThreshold)  
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
                if l in inDeg and inDeg[l] >= citationThreshold:
                    labels.append(1)
                else:
                    labels.append(-1)
        C.labels = labels
        collections.append(C)

    #join and return as single collection
    C = collection.join(collections)
    return [C, citationThreshold]

def trainAndTest(citationNetwork,trainstart,trainend,predictstart,predictend,citationMonths,citationThreshold,args):
    '''Train and test classifier.  Return prediction statistics'''
    if args.naivebayes: 
        classifier = naiveBayes.NaiveBayes() 
    elif args.svm:
        classifier = SVMLight.SVM() 
    else:
        print "No classifier specified."
        return 

    #Preparing data...
    TRAIN, citationThreshold = loadAndLabel(citationNetwork, args.root, trainstart, trainend, citationMonths, citationThreshold, args.regression)
    TEST, citationThreshold = loadAndLabel(citationNetwork, args.root, predictstart, predictend, citationMonths, citationThreshold, args.regression)

    #normalize feature vectors for SVM
    if args.svm:
        TRAIN.normalize()
        TEST.normalize()
        
    #classifying data...
    classifier.learn(TRAIN,options=args.options)
    predictions = classifier.classify(TEST,regression=args.regression)

    if args.regression:
        #baseline = TRAIN.averageLabel()
        results = utils.report_regression(TEST.labels,predictions,epsilon=args.epsilon)
    else:
        results = utils.report(TEST.labels,  predictions, TRAIN.majorityLabel()) 
    return results

def experiment0(args, N):
    
    print '\nTRAINING RANGE: {0} -> {1}'.format(args.trainstart, args.trainend)
    print 'PREDICTION RANGE: {0} -> {1}'.format(args.predictstart,  args.predictend)
    return  trainAndTest(N,args.trainstart, args.trainend, args.predictstart, args.predictend,args.citationMonths,args.citationThreshold,args)

def experiment1(args, N):

    results = dict()

    mvals = [6,12,24]
    wvals = [6,12,24]

    for m in mvals:
         for w in wvals:
             results[(m,w)]=[]

    for m in mvals:
        for w in wvals:
            print"\n**************"
            print "M={0} W={1}".format(m,w)
            print"****************\n"

            #predict citations for each month based on previous year
            for yymm in utils.dateRange(args.predictstart,args.predictend):
                trainstart = utils.addMonths(yymm,-(w+args.predictbuffer))
                trainend = utils.addMonths(yymm,-args.predictbuffer)
                predictstart = yymm
                predictend = utils.addMonths(yymm,1) 
                #ps.append(yymm)
                print '\nTRAINING RANGE: {0} -> {1}'.format(trainstart, trainend)
                print 'PREDICTION RANGE: {0} -> {1}'.format(predictstart, predictend)
                r = trainAndTest(N,trainstart, trainend, predictstart, predictend,m,args.citationThreshold,args)
                r['trainstart']= trainstart
                r['trainend']=trainend
                r['predictstart']=predictstart
                r['predictend']=predictend
                results[(m,w)].append( r )

if __name__ == '__main__':
    '''
    The main program
    '''
    #parse inputs
    parser = ArgumentParser()
    parser.add_argument("main")
    parser.add_argument("-root", "--root",help="Root directory of document feature vectors (one file per month)", default='../data/hep-th-svm/')
    parser.add_argument("-citation", "--citationData",help="Location of citation network data.", default='../data/cit-hep-th.txt')
    parser.add_argument("-ts","--trainstart",help="Specify start date of training documets.  Eg '9501' ")
    parser.add_argument("-te","--trainend",help="Specify end date of training documets.  Eg '9601' ")
    parser.add_argument("-tw","--trainwindow",help="Specify the size of the trainging period.  Eg 12 ", type=int)
    parser.add_argument("-pb","--predictbuffer",help="Specify the seperation between training and test data.  Eg 12 ", type=int, default=0)
    parser.add_argument("-ps","--predictstart",help="Specify start date of prediction documets.  Eg '9501' ")
    parser.add_argument("-pe","--predictend",help="Specify end date of prediction documets.  Eg '9601' ")
    parser.add_argument("-t","--citationThreshold",help="Citation count threshold.", type=int)
    parser.add_argument("-m","--citationMonths",help="Number of citationMonths used in tabulation of article citations.", type=int)
    parser.add_argument("-svm","--svm",help="Predict with support vector machine", action="store_true")
    parser.add_argument("-r","--regression",help="Perform regression based analysis. Only valid for svm", action="store_true")
    parser.add_argument("-ep","--epsilon",help="Regression tollerence.  Only relevent  for svm regression", type=int, default=1)
    parser.add_argument("-o","--options",help="Optional parameter string for SVM classifier.  Ignored by naive bayes classifier.", type=str, default='')
    parser.add_argument("-nb","--naivebayes",help="Prediict with naive bayes.", action="store_true")
    parser.add_argument("-0","--e0",help="Perform basic classification with given paramters", action="store_true")
    parser.add_argument("-1","--e1",help="Run experiment with loop over t (citation accumulation windoow) and w (duration of trianing data)", action="store_true")
    parser.add_argument("-s","--save",help="Save results to file (as pickled dict)", action="store_true")

    args = parser.parse_args(sys.argv)

    if args.regression:
        args.options+=' -z r'

    #Load citation network for later use
    N = citationNetwork.CitationNetwork()
    N.load(args.citationData)
    
    if args.e0:
        results = experiment0(args,N)
    elif args.e1:
        results = experiment1(args, N)

    #save results labels
    if args.save:
        datestring =  str(dt.datetime.now()).replace(' ','_')
        method = 'regression' if args.regression else 'binary'
        filename = method + '.{0}-{1}.{2}'.format(args.predictstart,args.predictend, datestring)

        f = open('../results/'+ filename+'.pickle', 'w')
        data = {'results':results,'metadata':args }
        pickle.dump(data,f)
        f.close


