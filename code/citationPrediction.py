'''
@created: Nov 6, 2013
@author: homoflashmanicus
@description: Command line tool for predicting citation counts of articles.  Perform various experiments. See below.
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

def loadAndLabel(network,root,start,end,nMonths,citationThreshold=None,args=None):
    '''
    Load collections for each from start month to end month, inclusively.
    Add citation counts for each article obtained in in the first nMonths of it's publication.
    Merge collections into a single collection object and return.
    '''

    collections = []
    for yymm in utils.dateRange(start,end):
        #Load article data in root/<yymm>.svm 
        C = collection.Collection()
        if args.svm:
            C.load(root+yymm+'.svm',normalize=True)
        else:
            C.load(root+yymm+'.svm',normalize=False)
        
        #Get inDegree of articles in the first nMonths of publication for the current (yymm) collection of articles.
        inDeg = network.inDegree(start=yymm,end=utils.addMonths(yymm,nMonths))
        inDeg = network.toDict(inDeg)
        inDeg = network.filterByDate(inDeg,start=yymm,end=utils.addMonths(yymm,1))

        #Attach labels to articles
        #NOTE: Some articles do not appear in the citation network data.  Such articles received zero citations.
        labels = []
        for l in C.labels:
            if l in inDeg:
                labels.append(inDeg[l])
            else:
                labels.append(0)
        C.labels = labels
        collections.append(C)

    #join and return as single collection
    C = collection.join(collections)

    #convert to binary label if not regression:
    if not args.regression:
        if citationThreshold==None:
            #Get threshold that best splits citation counts 
            citationThreshold = sorted(C.labels)[C.nDocs/2]
            print 'Computed Citation Threshold: ' + str(citationThreshold)
            nPos =  sum( 1 if l > citationThreshold else 0 for l in C.labels)
            print 'N > threshold: ' + str(nPos)
            print 'N <= threshold: ' + str( C.nDocs - nPos) + '\n'

        bin_labels=[]
        for l in C.labels:
            if l  > citationThreshold:
                bin_labels.append(1)
            else:
                bin_labels.append(-1)
        C.labels=bin_labels

    return [C, citationThreshold]

def trainAndTest(citationNetwork,trainstart,trainend,predictstart,predictend,citationMonths,citationThreshold,args,TRAIN=None,TEST=None):
    '''Train and test classifier.  Return prediction statistics'''

    #Preparing data...
    if not TRAIN:
        TRAIN, citationThreshold = loadAndLabel(citationNetwork, args.root, trainstart, trainend, citationMonths, citationThreshold, args)
    if not TEST:
        TEST, citationThreshold = loadAndLabel(citationNetwork, args.root, predictstart, predictend, citationMonths, citationThreshold, args)

    #set classifier
    if args.naivebayes: 
        classifier = naiveBayes.NaiveBayes() 
    elif args.svm:
        classifier = SVMLight.SVM() 
    else:
        print "No classifier specified."
        return 

    #classifying data...
    classifier.learn(TRAIN,options=args.options)
    predictions = classifier.classify(TEST,regression=args.regression)

    if args.regression:
        #baseline = TRAIN.averageLabel()
        results = utils.report_regression(TEST.labels,predictions,epsilon=args.epsilon)
    else:
        results = utils.report(TEST.labels,  predictions, TRAIN.majorityLabel())

    results['threshold']=citationThreshold

    return results

def experiment0(args, N):
    '''Simple classification on input parameters'''
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
            print "T={0} W={1}".format(m,w)
            print"****************\n"

            #predict citations for each month based on previous year
            for yymm in utils.dateRange(args.predictstart,args.predictend):
                trainstart = utils.addMonths(yymm,-(w+args.predictbuffer))
                trainend = utils.addMonths(yymm,-args.predictbuffer)
                predictstart = yymm
                predictend = utils.addMonths(yymm,1) 

                print '\nTRAINING RANGE: {0} -> {1}'.format(trainstart, trainend)
                print 'PREDICTION RANGE: {0} -> {1}'.format(predictstart, predictend)

                r = trainAndTest(N,trainstart, trainend, predictstart, predictend,m,args.citationThreshold,args)
                r['trainstart']= trainstart
                r['trainend']=trainend
                r['predictstart']=predictstart
                r['predictend']=predictend
                results[(m,w)].append( r )

    return results

def experiment2(args, N):

    results = dict()
    bvals = range(0,37,6)

    for b in bvals:
        results[b]=[]

    for b in bvals:

        print '\n********************'
        print ' b = {0}'.format(b)
        print '*********************\n'
        
        for yymm in utils.dateRange(args.predictstart,args.predictend):
            trainstart = utils.addMonths(yymm,-(args.trainwindow+b))
            trainend = utils.addMonths(yymm,-b)
            predictstart = yymm
            predictend = utils.addMonths(yymm,1) 
            print '\nTRAINING RANGE: {0} -> {1}'.format(trainstart, trainend)
            print 'PREDICTION RANGE: {0} -> {1}'.format(predictstart, predictend)
            r = trainAndTest(N,trainstart, trainend, predictstart, predictend, args.citationMonths, args.citationThreshold, args)
            r['trainstart']= trainstart
            r['trainend']=trainend
            r['predictstart']=predictstart
            r['predictend']=predictend
            results[b].append( r )
    return results

def experiment3(args, N):

    results = dict()
    bvals = range(0,37,6)
    
    for b in bvals:
        results[b]=[]

    for yymm in utils.dateRange(args.trainstart, args.trainend):
        trainstart = yymm
        trainend = utils.addMonths(yymm,args.trainwindow)
        print '\nTRAINING RANGE: {0} -> {1}'.format(trainstart, trainend)
        args.citationThreshold = None
        TRAIN, citationThreshold = loadAndLabel(N, args.root, trainstart,trainend,args.citationMonths,args.citationThreshold, args)

        for b in bvals:

            print '\n********************'
            print ' b = {0}'.format(b)
            print '*********************\n'

            predictstart = utils.addMonths(trainend,b)
            predictend = utils.addMonths(trainend,1+b) 
            print 'PREDICTION RANGE: {0} -> {1}'.format(predictstart, predictend)
            r = trainAndTest(N,trainstart, trainend, predictstart, predictend, args.citationMonths, citationThreshold, args,TRAIN=TRAIN)
            r['trainstart']= trainstart
            r['trainend']=trainend
            r['predictstart']=predictstart
            r['predictend']=predictend
            results[b].append( r )
    return results

def experiment4(args, N):
    '''Very c value for svm classifier.'''
    args.svm=True
    results = dict()

    #for c in [10,15,19,20,22,24,26,30,35,45,60]: # c-values for title/abstract data set 
    for c in [500, 550,600,650,660,675,680,690,700]: # c-values for full text data set

        print '\n*********************'
        print 'SVM with C = ' + str(c)
        print '*********************\n'

        args.options = "-c " + str(c)
        results[c]=[]

        #predict citations for each month based on previous year
        for yymm in utils.dateRange(args.predictstart,args.predictend):
            trainstart = utils.addMonths(yymm,-(args.trainwindow+args.predictbuffer))
            trainend = utils.addMonths(yymm,-args.predictbuffer)
            predictstart = yymm
            predictend = utils.addMonths(yymm,1) 

            print '\nTRAINING RANGE: {0} -> {1}'.format(trainstart, trainend)
            print 'PREDICTION RANGE: {0} -> {1}'.format(predictstart, predictend)

            r = trainAndTest(N,trainstart, trainend, predictstart, predictend, args.citationMonths, args.citationThreshold,args)
            r['trainstart']= trainstart
            r['trainend']=trainend
            r['predictstart']=predictstart
            r['predictend']=predictend
            results[c].append( r )

    return results

def experiment5(args,N):
    ''''sample classifier over one month test sets from args.predictstart to args.predictend.  training window is determined by other args.'''

    results = []

    for yymm in utils.dateRange(args.predictstart,args.predictend):
        trainstart = utils.addMonths(yymm,-(args.trainwindow +args.predictbuffer))
        trainend = utils.addMonths(yymm,-args.predictbuffer)
        predictstart = yymm
        predictend = utils.addMonths(yymm,1) 

        print '\nTRAINING RANGE: {0} -> {1}'.format(trainstart, trainend)
        print 'PREDICTION RANGE: {0} -> {1}'.format(predictstart, predictend)

        r = trainAndTest(N,trainstart, trainend, predictstart, predictend, args.citationMonths ,args.citationThreshold,args)
        r['trainstart']= trainstart
        r['trainend']=trainend
        r['predictstart']=predictstart
        r['predictend']=predictend
        results.append( r )

    return results

def experiment6(args,N):
    '''Leave one month out classifier test.'''

    results = []

    for yymm in utils.dateRange(args.trainstart,args.trainend):

        trainrangeL = utils.dateRange(args.trainstart,yymm)
        trainrangeR = utils.dateRange(utils.addMonths(yymm,1), args.trainend)

        TRAINL = collection.Collection()
        TRAINR = collection.Collection()
        
        citationThreshold = args.citationThreshold
        if len(trainrangeL)>0: 
            trainstartL = trainrangeL[0]
            trainendL = yymm
            print 'TRAIN RANGE LEFT: {0} -> {1}'.format(trainstartL, trainendL)
            TRAINL, citationThreshold = loadAndLabel(N, args.root, trainstartL,trainendL,args.citationMonths,citationThreshold,args)

        if len(trainrangeR)>0: 
            trainstartR = utils.addMonths(yymm,1)
            trainendR = args.trainend
            print 'TRAIN RANGE RIGHT: {0} -> {1}'.format(trainstartR, trainendR)
            TRAINR, citationThreshold = loadAndLabel(N, args.root, trainstartR,trainendR,args.citationMonths,citationThreshold,args)
        
        TRAIN = collection.join([TRAINL,TRAINR])

        trainstart = args.trainstart
        trainend = args.trainend
        predictstart = yymm
        predictend = utils.addMonths(yymm,1) 

        print 'PREDICTION RANGE: {0} -> {1}'.format(predictstart, predictend)

        r = trainAndTest(N,trainstart, trainend, predictstart, predictend, args.citationMonths ,citationThreshold,args,TRAIN=TRAIN)
        r['trainstart']= trainstart
        r['trainend']=trainend
        r['predictstart']=predictstart
        r['predictend']=predictend
        results.append( r )

    return results



if __name__ == '__main__':
    '''
    The main program
    '''
    #parse inputs
    parser = ArgumentParser()
    parser.add_argument("main")
    
    #data location
    parser.add_argument("-root", "--root",help="Root directory of document feature vectors (one file per month)", default='../data/hep-th-svm/')
    parser.add_argument("-citation", "--citationData",help="Location of citation network data.", default='../data/cit-hep-th.txt')
    
    #parameters
    parser.add_argument("-ts","--trainstart",help="Specify start date of training documets.  Eg '9501' ")
    parser.add_argument("-te","--trainend",help="Specify end date of training documets.  Eg '9601' ")
    parser.add_argument("-tw","--trainwindow",help="Specify the size of the trainging period.  Eg 12 ", type=int)
    parser.add_argument("-pb","--predictbuffer",help="Specify the seperation between training and test data.  Eg 12 ", type=int, default=0)
    parser.add_argument("-ps","--predictstart",help="Specify start date of prediction documets.  Eg '9501' ")
    parser.add_argument("-pe","--predictend",help="Specify end date of prediction documets.  Eg '9601' ")
    parser.add_argument("-t","--citationThreshold",help="Citation count threshold.", type=int)
    parser.add_argument("-m","--citationMonths",help="Number of citationMonths used in tabulation of article citations.", type=int)

    #svm
    parser.add_argument("-svm","--svm",help="Predict with support vector machine", action="store_true")
    parser.add_argument("-r","--regression",help="Perform regression based analysis. Only valid for svm", action="store_true")
    parser.add_argument("-ep","--epsilon",help="Regression tollerence.  Only relevent  for svm regression", type=int, default=1)
    parser.add_argument("-o","--options",help="Optional parameter string for SVM classifier.  Ignored by naive bayes classifier.", type=str, default='')

    #nb
    parser.add_argument("-nb","--naivebayes",help="Prediict with naive bayes.", action="store_true")

    #primary modes of operation
    parser.add_argument("-0","--e0",help="Perform basic classification with given paramters", action="store_true")
    parser.add_argument("-1","--e1",help="Run experiment with loop over t (citation accumulation windoow) and w (duration of trianing data)", action="store_true")
    parser.add_argument("-2","--e2",help="Run experiment with loop over seperation distance between training and test data, for fixed test set", action="store_true")
    parser.add_argument("-3","--e3",help="Run experiment with loop over seperation distance between training and test data, for fixed training set", action="store_true")
    parser.add_argument("-4","--e4",help="Run experiment with loop over c value for svm", action="store_true")
    parser.add_argument("-5","--e5",help="Run experument with loop over single months between predict start and predict end ", action="store_true")
    parser.add_argument("-6","--e6",help="Run experument with leave one month out error", action="store_true")
    
    #save
    parser.add_argument("-s","--save",help="Save results to file (as pickled dict)", action="store_true")

    args = parser.parse_args(sys.argv)

    if args.regression:
        args.options+=' -z r'

    #Load citation network for later use
    N = citationNetwork.CitationNetwork()
    N.load(args.citationData)
    

    #Perform differnt kinds of experiments
    ex = None
    if args.e0:
        ex = 0
        results = experiment0(args,N)
    elif args.e1:
        ex = 1
        results = experiment1(args, N)
    elif args.e2:
        ex = 2
        results = experiment2(args, N)
    elif args.e3:
        ex = 3
        results = experiment3(args, N)
    elif args.e4:
        ex = 4
        results = experiment4(args, N)
    elif args.e5:
        ex = 5
        results = experiment5(args, N)
    elif args.e6:
        ex = 6
        results = experiment6(args, N)



    #save results labels
    if args.save:
        datestring =  str(dt.datetime.now()).replace(' ','_').replace(':','-')
        method = 'regression' if args.regression else 'binary'
        classifier = 'svm' if args.svm else 'nb'
        fileType = 'ta' if args.root.find('.ta') >= 0 else 'full'
        filename = method + '.{0}.{1}.ex{2}.'.format(classifier,fileType,ex)+ '{0}-{1}.{2}'.format(args.predictstart,args.predictend, datestring)

        f = open('../results/'+ filename+'.pickle', 'w')
        data = {'results':results,'metadata':args }
        pickle.dump(data,f)
        f.close

