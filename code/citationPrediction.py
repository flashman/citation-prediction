'''
@created: Nov 6, 2013
@author: homoflashmanicus
@description: Predict citation counts of articles.
'''

import sys
from argparse import ArgumentParser

import utils
import collection
import citationNetwork
import naiveBayes

def loadAndLabel(network,root,start,end,nMonths=12,threshold=10):
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
            if l in inDeg and inDeg[l] >= threshold:
                labels.append(1)
            else:
                labels.append(-1)
        C.labels = labels
        print len( [l for l in labels if l>0 ])
        collections.append(C)

    #join and return as single collection
    return collection.join(collections)

if __name__ == '__main__':
    '''
    The main program
    '''

    #parse inputs
    parser = ArgumentParser()
    parser.add_argument("main")
    parser.add_argument("root",help="Root directory of document feature vectors (one file per month)", default='../data/hep-th-svm/')
    parser.add_argument("citation",help="Location of citation network data.", default='../data/cit-hep-th.txt')
    parser.add_argument("-s","--start",help="Specify start date of documets to be considered.  Eg '9501' ")
    parser.add_argument("-e","--end",help="Specify end date of documets to be considered.  Eg '9601' ")
    parser.add_argument("-m","--months",help="Number of months used in tabulation of article citations.", type=int, default=12)
    args = parser.parse_args(sys.argv)

    
    N = citationNetwork.CitationNetwork()
    N.load(args.citation)

    C = loadAndLabel(N, args.root, args.start, args.end, args.months)
    D = loadAndLabel(N, args.root, utils.addMonths(args.end,1+args.months), utils.addMonths(args.end,2+args.months), args.months)


    NB = naiveBayes.NaiveBayes()
    NB.train(C.labels, C.M)
    predictions = NB.test(D.M)
    NB.report(D.labels, predictions) 

    

