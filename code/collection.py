'''
@created: Nov 6, 2013
@author: homoflashmanicus
@description: manage collection of documents.
'''

import scipy.sparse as sps
from itertools import izip
class Collection:
    
    def __init__(self,fileLocation=None):
        self.fileLocation=fileLocation
        self.nVocab=0
        self.nDocs=0
        self.labels=[]
        self.ids=[]
        self.M=None
        if self.fileLocation!=None:
            self.load(self.fileLocation)

    def load(self,fileLocation,count=True,normalize=True):
        '''Load svmlight formatted data in label array and csr sparse matrix (row=doc_id, col=word_id)'''

        self.fileLocation = fileLocation

        f=open(fileLocation)
        raw = f.read()
        f.close()

        ndocs=0
        count=[]
        row=[]
        col=[]
        labels=[]

        for line in raw.splitlines():
            line = line.split()
            l = line[0]
            labels.append(l)
            #nWords = float(sum(int(f.split(':')[1]) for f in line[1:]))
            for feature in line[1:]:
                kv = feature.split(':')
                key = int(kv[0])
                val = int(kv[1])
             #   if normalize: val = val/nWords 
                if not count: val = 1
                row.append(ndocs)
                col.append(key)
                count.append(val)
            ndocs+=1

        self.set(sps.csr_matrix((count, (row,col))) , labels)

    def set(self,matrix,labels):
        '''
        Set collection data from sparse matrix and labels
        '''
        self.M = matrix
        self.labels =labels
        self.nDocs = self.M.shape[0]
        self.nVocab = self.M.shape[1]
        

    def save(self,filename):
        '''
        Save collection to file with svm format.
        If collection were loaded from an existing file, than just save by copying from that file directly.
        If not, then build lines directly from matrix
        '''
        if self.fileLocation != None:
            f=open(self.fileLocation)
            raw = f.read()
            f.close()

            f=open(filename, 'w')
        
            for label, line in izip(self.labels, raw.splitlines()):
                if label != None:
                    line = line.split()
                    line[0] = str(label)
                    line = ' ' .join(line)
                f.write(line+'\n')
            f.close()
        else:
            f=open(filename, 'w')
            for i, label in enumerate(self.labels):
                if label != None:
                    row = self.M[i,:]
                    line = []
                    line.append( str(label) )
                    for k,v in izip(row.indices, row.data ):
                        line.append(':'.join([ str(k),str(v)]))
                    line = ' ' .join(line)
                f.write(line+'\n')
            f.close()

    def join(self, collection):
        '''
        Append collection to self.
        '''
        self.labels.extend(collection.label)
        
        nVocab = max(self.nVocab, collection.nVocab)
        self.M._shape = (self.nDocs,nVocab)
        collection.M._shape = (collection.nDocs,nVocab)

        self.M = sps.vstack( [self.M, collection.M], format='csr')
        self.nVocab=nVocab
        self.nDocs=self.M.shape[0]

    def removeStopWords(self, threshold = 0.9):
        '''
        Remove words that appear in more than threshold (% or int) of documents. 
        Defaults to 90%
        '''
        if type(threshold) == float:
            if threshold <= 1.0:
                threshold = int(self.nDocs * threshold)
            else:
                threshold = int(threshold)

    def removeInfrequentWords(self, threshold=2):
        '''
        Remove words that appear in less than threshold (% or int) of documents.
        Defaults to 2 documents.
        '''        
#        keepCols = [i for i,v in enumerate(self.M.sum(0).A1) if v>=threshold ] 
#        self.nVocab = len(keepCols)
#        self.M = self.M[:,keepCols]

def join(collectionList):
    '''
    Create new collection object from all the collection in collection list.
    '''
    
    #Find collection collection with largest vocabulary
    nVocab = max( arts.nVocab for arts in collectionList )

    #standerdize dimensions and stack matrices
    MS = [arts.M for arts in collectionList]
    for M in MS:
        M._shape = (M.shape[0], nVocab)
    M = sps.vstack(MS, format='csr')

    #concatenate label lists
    labels = []
    for arts in collectionList:
        labels.extend(arts.labels)

    #build new collection object
    collection = Collection()
    collection.set(M,labels)

    return collection
