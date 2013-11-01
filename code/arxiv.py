'''
Created on Jan 14, 2013
@author: homoflashmanicus
'''

import os
import re
import gzip
from collections import defaultdict
from itertools import izip

GZ = re.compile('.*\.gz$')
ARXIVFN = re.compile('^[0-9]{4,}\.(txt|prep)(?:\.gz)?$')
FN2ID = re.compile('([0-9]{4}[\.]*[0-9]*)\..*')
PRE2000 = re.compile('^[5-9][0-9].*')
POST2000 = re.compile('^[0-4][0-9].*')

class ArxivReader:
    '''
    The arxiv class generates and/or manages 'n-gram counts per month' data for all articles of a collection.
    '''
    def __init__(self, root = None, start = None, end = None, dbdir = None):
        '''
        Constructor
        '''
        self.__attributes__ = ['__offset__', 'dbdir', 'start', 'end', 'N', 'A', 'W', 'M']  # attribute list
        self.__offset__ = len(self.__attributes__)                                         # database file offset

        self.root = root         # path to data directory 
        self.start = start        # start time, eg '9501'
        self.end = end          # end time, eg '0512'
        self.N = 0               # total number of words
        self.A = 0               # total number of articles
        self.W = 0               # total number of unique words                                                                                                    
        self.M = 0               # total number of months
        self.index = dict()      # map: word -> index
        self.word = list()       # map: index -> word
        self.wordset = set()     # for fast membership check
        self.month = list()      # total number of words per month
        self.monthlabel = list() # months, eg March 2005 -> '0503'
        self.dbdir = dbdir       # path to database storage (for now, a text file) 
        self.db = None           # database connection (for now, the text file at self.dbdir)
        
        if (self.root and not self.dbdir):
            self.load_from_root()
        elif(self.dbdir):
            self.load_from_db()
    
    def __datehelper__(self,s):
        if PRE2000.match(s):
            return '19'+s
        elif POST2000.match(s):
            return '20'+s
        else:
            return s

    def __datecomp__(self,s,t):
        if PRE2000.match(s) and POST2000.match(t):
            return True
        elif POST2000.match(s) and PRE2000.match(t):
            return False
        else:
            return s<=t
    
    def load_from_root(self,root = None, start = None, end = None):
        if root: self.root = root
        if start: self.start = start
        if end: self.end = end

        fns=[]
        for dirname, dirnames, filenames in os.walk(self.root):
            dirnames = filter(
                              lambda s: self.__datecomp__(self.start,s) 
                              and self.__datecomp__(s,self.end), dirnames
                              )
            for filename in filenames:
                if ARXIVFN.match(filename):
                    ID = FN2ID.findall(filename)[0]
                    yymm = ID[:4]
                    if self.start and not self.__datecomp__(self.start,yymm):
                        continue
                    if self.end and not self.__datecomp__(yymm,self.end):
                        continue
                    fns.append((dirname,filename))
        filenames = sorted(fns,key=lambda(d,f):self.__datehelper__(f))
        
        #create local variable for efficiency
        N = 0
        A = 0
        W = 0
        M = 0
        index = dict()
        word = list()
        wordset = set()
        month = list()
        monthlabel = list()
        db = list()

        if GZ.match(filenames[0][1]):
            fopen=gzip.open
        else:
            fopen=open
        
        #parse data files
        for filename in filenames:
            f = fopen(os.path.join(filename[0], filename[1]))
            raw = f.read()
            f.close()
            month.append(0)
            for line in raw.splitlines():
                line = line.split(',')
                A+=1
                for p in xrange(3,len(line),2):
                    try:
                        key,val=line[p],int(line[p+1])
                    except:
                        continue
                    N+=val
                    month[M]+=val
                    if key in wordset:
                        i = index[key]
                    else:
                        i = W
                        index[key]=i
                        word.append(key)
                        wordset.add(key)
                        db.append(defaultdict(int))
                        W+=1
                    j = M   
                    db[i][j]+=val
            ID = FN2ID.findall(filename[1])[0]
            yymm = ID[:4]
            monthlabel.append(yymm)
            M+=1

        if not self.start:
            self.start = monthlabel[0]
        if not self.end:
            self.end = monthlabel[-1]

        #save tabulated data to file
        dbdir = self.root
        if self.start: dbdir += '-' + self.start
        if self.end: dbdir += '-' + self.end
        dbdir += '.db.gz'
        dbf = gzip.open(dbdir,'wb')

        #header
        for attr in self.__attributes__:
            l  = attr + ',' + str(getattr(self, attr)) 
            dbf.write(l + '\n')
        #DB
        for w, row in izip(word,db):
            l = w + ',' + ','.join(str(key)+','+str(val) for key,val in row.iteritems())
            dbf.write( l + '\n')
        dbf.close()
        del db

        #set model parameters
        self.N = N
        self.A = A
        self.W = W
        self.M = M
        self.index = index
        self.word = word
        self.wordset = wordset
        self.monthlabel = monthlabel
        self.month = month
        self.dbdir = dbdir

    def getWordsAppearingAfter(self,yymm,minCount=1):
        self.connect()
        words = []
        counts = []
        for i,l in enumerate(self.db):
            line = l.split(',')
            word = line[0]
            if yymm <= int(line[1]):  #self.__datecomp__( yymm, self.monthlabel[ int(line[1]) ]):
                c = sum(int(line[i]) for i in xrange(2,len(line),2))
                if c>=minCount:
                    words.append(word)
                    counts.append(c) 
        self.disconnect()

        return [words, counts]

    def getArticelsContaining(self,words,minCount=1,subject=False):
        articleIDs = []
        fns=[]
        for dirname, dirnames, filenames in os.walk(self.root):
            dirnames = filter(
                              lambda s: self.__datecomp__(self.start,s) 
                              and self.__datecomp__(s,self.end), dirnames
                              )
            for filename in filenames:
                if ARXIVFN.match(filename):
                    ID = FN2ID.findall(filename)[0]
                    yymm = ID[:4]
                    if self.start and not self.__datecomp__(self.start,yymm):
                        continue
                    if self.end and not self.__datecomp__(yymm,self.end):
                        continue
                    fns.append((dirname,filename))
        filenames = sorted(fns,key=lambda(d,f):self.__datehelper__(f))

        if GZ.match(filenames[0][1]):
            fopen=gzip.open
        else:
            fopen=open
        
        #parse data files
        for filename in filenames:
            f = fopen(os.path.join(filename[0], filename[1]))
            raw = f.read()
            f.close()
            for line in raw.splitlines():
                line = line.split(',')
                aid = line[0]
                for p in xrange(3,len(line),2):
                    try:
                        key,val=line[p],int(line[p+1])
                    except:
                        continue
                    if val >= minCount and key in words:
                        if subject:
                            aid = aid.split('/')[1]
                        articleIDs.append(aid)
                        break
        return set(articleIDs)

    def connect(self, mode = 'rb'):
        if self.dbdir:
            self.db = gzip.open(self.dbdir, mode)
            i=0
            while i < self.__offset__:
                self.db.readline()
                i+=1

    def disconnect(self):
        if self.db:
            self.db.close()

    def rewind(self):
        if self.db:
            self.db.rewind()
            i=0
            while i < self.__offset__:
                self.db.readline()
                i+=1 
