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
def report(labels,predictions,verbose=True):
    nPos = sum(1 for l in labels if l>0)
    nNeg = sum( 1 for l in labels if l<0 )
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

    errorRate = 1.0*errors/len(labels)
    naiveErrorRate = 1.0 - 1.0*max(nPos,nNeg)/len(labels) 

    if verbose:
        print "Documents classified: " + str(len(labels))
        print "Total Positive: " + str(nPos)
        print "Total Negative: " + str(nNeg)
        print "True Positives: " + str(truePos) 
        print "True Negatives: " + str(trueNeg) 
        #print "False Positives: " + str(falsePos)
        #print "False Negatives: " + str(falseNeg)
        #print "Errors: " + str(errors)
        print "Error rate: " + str( errorRate)
        print "Niave error rate: " + str(naiveErrorRate)
    return [errorRate, naiveErrorRate,nPos,nNeg,truePos,trueNeg,falsePos,falseNeg]
