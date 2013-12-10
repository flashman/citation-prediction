'''
@created: Dec 7, 2013
@author: homoflashmanicus
@description: Clean SVM data.  Remove stop words and infrequent words
'''

import os
import gzip
import utils

DATADIR = '../data/hep-th-svm.ta/'
#RESULTSDIR = '../data/hep-th-svm.cleaned.ta/'
RESULTSDIR = '../data/hep-th-svm.cleaned.ta.forStats/'


MINWORDFREQ = 3
MAXDOCFREQ = 0.9
MINDOCFREQ = 1

vocabularyCount = dict()
vocabularyDocCount = dict()
skipVocabulary =set()
nDocs = 0

#gather list of filenames for all data
fns=[]
for dirname, dirnames, filenames in os.walk(DATADIR):
    for filename in filenames:
        if filename.endswith('.svm'):
            fns.append((dirname,filename))

#sort files in ascending order
filenames = sorted(fns,key=lambda(d,f): utils.datehelper(f))

#generate word stats
for filename in filenames:

    if utils.GZ.match(filename[1]):
        fopen = gzip.open
    else:
        fopen = open

    #read data file
    f = fopen(os.path.join(filename[0], filename[1]))
    raw = f.read()
    f.close()

    for line in raw.splitlines():
        line = line.split(' ')
        nDocs +=1
        for kv in line[1:]:
            k,v= kv.split(':')
            v=int(v)
            if k not in vocabularyCount:
                vocabularyCount[k]=v
                vocabularyDocCount[k]=1
            else:
                vocabularyCount[k]+=v
                vocabularyDocCount[k]+=1

#find infrequent words
for k,v in vocabularyCount.iteritems():
    if v<=MINWORDFREQ:
        skipVocabulary.add(k)

#find very frequent words
for k,v in vocabularyDocCount.iteritems():
    if 1.0*v/nDocs >= MAXDOCFREQ or v<=MINDOCFREQ:
        skipVocabulary.add(k)

print "ORIGINAL Vocabulary Size: " + str( len(vocabularyCount.keys()) )

print "REMOVING " + str(len(skipVocabulary)) + " WORDS FROM THE COLLECTION..."

print "FINAL Vocabulary Size: " + str( len(vocabularyCount.keys()) - len(skipVocabulary) )

#save  acceptible words as svm
for filename in filenames:

    if utils.GZ.match(filename[1]):
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
        line = line.split(' ')
        arxiv_id = line[0]
        svmline=[]
        for kv in line[1:]:
            k,v=kv.split(':')
            if k not in skipVocabulary:
                svmline.append(':'.join([k,v]))
        svmline = [arxiv_id] + sorted(svmline, key = lambda(d): int(d.split(':')[0])) 
        fsvm.write(' '.join(svmline) + '\n')
    fsvm.close()
