'''
@created: Nov 1, 2013
@author: homoflashmanicus
@description: utility functions
'''

import re
import time

from itertools import izip

GZ = re.compile('.*\.gz$')
ARXIVFN = re.compile('^[0-9]{4,}\.(txt|prep)(?:\.gz)?$')
PRE2000 = re.compile('^[5-9][0-9].*')
POST2000 = re.compile('^[0-4][0-9].*')

YEARS= [str(y)[2:4] for y in range(1993,2004)]
MONTHS =[str(m)[1:3] for m in range(101,113)]
YYMM = [yy+mm for yy in YEARS for mm in MONTHS][0:124]

#ARXIV ID/DATE UTILITY FUNCTIONS
def datehelper(s):
    if PRE2000.match(s):
        return '19'+s
    elif POST2000.match(s):
        return '20'+s
    else:
        return s

def datecomp(s,t):
    if PRE2000.match(s) and POST2000.match(t):
        return True
    elif POST2000.match(s) and PRE2000.match(t):
        return False
    else:
        return s<=t

def fixid( oid ):
    '''Standardized arxiv ids'''
    if len(oid) == 6:
        nid = '0' + oid
    elif len(oid) == 5:
        nid = '00' + oid
    elif len(oid) == 4:
        nid = '000' + oid
    else:
        nid = oid
    return nid

def addMonths(yymm, m):
    '''Add m months to yymm date string'''
    index = YYMM.index(yymm[0:4])
    return YYMM[index +m ] + yymm[4:]

def dateRange(start,end):
    try:
        sp = YYMM.index(start)
    except:
        sp = 0
    try:
        ep = YYMM.index(end)
    except:
        ep = len(YYMM)
    return YYMM[sp:ep]

#TIME UTILITY FUNCTIONS
def current_milli_time():
    return int(round(time.time() * 1000))

def current_micro_time():
    return int(round(time.time() * 1000000))

#REPORTING
def report(labels,predictions,verbose=True,majorityLabel=None):
    '''
    Report prediction success for binary learning task. Return error rate, precision, recall and naive error rate as a dict.  Also return a boolean vector indicating which predictions were correct.
    Baseline stores the the mojority rule lable (the majority label of the training data).
    '''
    total = 1.0*len(labels)
    falsePos=0 
    falseNeg=0
    truePos=0 
    trueNeg=0
    tf = []

    for p,l in izip(predictions,labels):
        if p!=l:
            tf.append(False)
            if l==1:
                falseNeg+=1
            else:
                falsePos+=1
        else:
            tf.append(True)
            if l==1:
                truePos+=1
            else:
                trueNeg+=1

    results = dict()
    results['documents'] = total
    results['errors'] = falsePos+falseNeg
    results['errorRate'] = 1.0*(falsePos+falseNeg)/total
    results['accuracy'] = 1.0*(truePos+trueNeg)/total
    results['precision'] = 1.0*truePos/max(truePos+falsePos,1.0)
    results['recall'] = 1.0*truePos/max(truePos+falseNeg,1.0)
    if majorityLabel:
        results['naive'] = 1.0*sum(1 for p in predictions if  p != majorityLabel)/total
    else:
        results['naive'] = 1.0*min(truePos+falseNeg,trueNeg + falsePos)/total
    results['tf']=tf
    results['labels']=labels
    results['predictions']=predictions
    
    if verbose:
        print "Documents classified: " + str(total)
        print "Errors: " + str(falsePos+falseNeg)
        print "Error rate: " + str(results['errorRate'])
        print "Accuracy: " + str(results['accuracy'])
        print "Precision: " + str(results['precision'])
        print "Recall: " + str(results['recall'])
        print "Baseline error rate: " + str(results['naive'])
    return results

def report_regression(labels,predictions,verbose=True,epsilon=1):
    '''
    report on regression based predictions
    '''
    total = 1.0*len(labels)
    sqdiff = []
    nOutliers = int(round(0.05*total))
    outlierThreshold =  sorted(labels)[-nOutliers]
    for p,l in izip(predictions,labels):
        d = p-float(l)
        ad = max(abs(d)-epsilon,0)
        sqdiff.append(ad**2 )
    avgsqdiff = sum(v for l,v in izip(labels, sqdiff) if l<outlierThreshold )/total #exclude outliers
    nOutliers = sum(1 for l in labels if l>=outlierThreshold)
    errors = sum( 1.0 for e in sqdiff if e>0)
    errorRate = errors/total

    results=dict()
    results['avgSqDiff']= avgsqdiff
    results['sqDiff']= sqdiff
    results['errors']=errors
    results['errorRate']=errorRate
    results['nOutliers']=nOutliers
    results['outlierThreshold']= outlierThreshold
    results['predictions']=predictions
    results['labels']= labels

    if verbose:
        print "Documents classified: " + str(total)
        print "Epsilon: " + str(epsilon)
        print "Errors: " + str(errors)
        print "Error Rate: " + str(errorRate)
        print "Avg Sq Diff: " + str(avgsqdiff)
        print "N Outliers: " + str(nOutliers)
        print "Outlier Threshold: " + str(outlierThreshold)
    return results
