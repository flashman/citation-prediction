'''
@created: Nov 1, 2013
@author: homoflashmanicus
@description: Convert prep formated arxiv data to svmlight format.  Addidtionally build dictionary 
'''

import os
import gzip
from utils import *

DATADIR = '../data/hep-th/'
RESULTSDIR = '../data/hep-th-svm-cleaned-2/'
FREQTHRESHOLD = 2

W = 1
vocabularyIndex = dict()
vocabulary = list()
vocabularySet = set()

#gather list of filenames for all data
fns=[]
for dirname, dirnames, filenames in os.walk(DATADIR):
    for filename in filenames:
        if ARXIVFN.match(filename):
            fns.append((dirname,filename))

#sort files in ascending order
filenames = sorted(fns,key=lambda(d,f):datehelper(f))

#build svmlight formated data 
for filename in filenames:

    if GZ.match(filename[1]):
        fopen = gzip.open
    else:
        fopen = open

    #read data file
    f = fopen(os.path.join(filename[0], filename[1]))
    raw = f.read()
    f.close()

    #open file for svm formatted data
    fsvm = open(os.path.join(RESULTSDIR,filename[1].split('.')[0]+'.svm'),'w')

    #transform lines to svm format
    for line in raw.splitlines():
        line = line.split(',')
        #arxiv_id = line[0] 
        arxiv_id = line[0].split('/')[1]
        svmline=[]
        for k,v in zip(line[3::2], line[4::2]):
            if int(v) >= FREQTHRESHOLD:
                if k in vocabularySet:
                    i = vocabularyIndex[k]
                else:
                    i = W
                    vocabularyIndex[k]=i
                    vocabularySet.add(k)
                    vocabulary.append(k)
                    W+=1
                svmline.append(':'.join([str(i),v]))
        svmline = [arxiv_id] + sorted(svmline, key = lambda(d): int(d.split(':')[0])) 
        fsvm.write(' '.join(svmline) + '\n')
    fsvm.close()

#save vocabulary to file
fvocab = open(os.path.join(RESULTSDIR,'vocabulary.txt'),'w')
for v in vocabulary:
    fvocab.write(v + '\n')
