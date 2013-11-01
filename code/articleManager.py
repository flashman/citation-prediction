'''
@created: Oct 29, 2013
@author: homoflashmanicus
@description: Python interface to postgres database of hep-th article content from Jan 1993-April 2003
@dependencies: postgresql9.1
'''

import sys
import os
import re
import gzip
import psycopg2 as pg
from argparse import ArgumentParser

#configuration constants for interfacing with postrgresql
DB_NAME = 'networks_dev'
USER = 'networks'
PW = 'networks'
HOST = 'localhost'

#location of raw data. necessary for rebuilding the articles table 
DATADIR='../data/hep-th'

GZ = re.compile('.*\.gz$')
ARXIVFN = re.compile('^[0-9]{4,}\.(txt|prep)(?:\.gz)?$')
PRE2000 = re.compile('^[5-9][0-9].*')
POST2000 = re.compile('^[0-4][0-9].*')

#UTILITY FUNCTIONS
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

def fixID(oid):
    if len(oid) == 6:
        nid = '0' + oid
    elif len(oid) == 5:
        nid = '00' + oid
    elif len(oid) == 4:
        nid = '000' + oid
    else:
        nid = oid
    return nid

class ArticleManager():
    '''Manage arxiv articicles in postgres database'''

    def __init__(self):
        self.DB_NAME = 'networks_dev'
        self.USER = 'networks'
        self.PW = 'networks'
        self.HOST = 'localhost'
        self.DATADIR='../data/hep-th'
        self.connect()
        
    def connect(self):
        self.db = pg.connect("dbname=" + DB_NAME + " user=" + USER + " password=" + PW + " host=" + HOST)
        self.cur = self.db.cursor()

    def disconnect(self):
        self.cur.close()
        self.db.close()

    def execute(self,query, args=None):
        if args==None:
            self.cur.execute(query)
        else:
            self.cur.execute(query, args)

    def load(self):
        self.cur.execute(" CREATE TABLE articles ( id char(7) NOT NULL, subject character varying(100), content tsvector, CONSTRAINT articles_pkey PRIMARY KEY (id) )")
        self.db.commit()

        #gather list of filenames
        fns=[]
        for dirname, dirnames, filenames in os.walk(DATADIR):
            for filename in filenames:
                if ARXIVFN.match(filename):
                    fns.append((dirname,filename))
        filenames = sorted(fns,key=lambda(d,f):datehelper(f))
        #handle gzipped data
        if GZ.match(filenames[0][1]):
            fopen=gzip.open
        else:
            fopen=open
        
        #parse data files
        for filename in filenames:
            f = fopen(os.path.join(filename[0], filename[1]))
            raw = f.read()
            f.close()
            print "Loading " + filename[0] + '/' + filename[1] + "..."
            for line in raw.splitlines():
                line = line.split(',')
                subject= line[0].split('/')[0]
                arxiv_id = line[0].split('/')[1]
                tsvector = [ k.replace(' ','') +':' + v for k,v in zip(line[3::2], line[4::2]) ]
                tsvector = ' '.join(tsvector)
                self.cur.execute("INSERT INTO articles (id,subject, content) VALUES (%s,%s,%s) ", (arxiv_id,subject,tsvector ))
            self.db.commit()

        print "Indexing articles...this could take a while"
        self.cur.execute(" CREATE INDEX articles_index ON articles USING gin(content); ")
        self.db.commit()
        

    def reload(self):
        self.cur.execute("DROP table articles")
        self.load()
        
    def search(self,queryString,count=False):
        queryString = queryString.replace(' ','')
        self.execute("SELECT id FROM articles WHERE content @@ %(qs)s::tsquery",{'qs':queryString})
        if count:
            return len(self.cur.fetchall())
        else:
            return [v[0] for v in self.cur.fetchall()]

if __name__ == '__main__':
    '''
    The main program
    '''

    #parse inputs
    parser = ArgumentParser()
    parser.add_argument("main")
    parser.add_argument("-l","--load",help="Use flag when loading from scratch",action="store_true")
    parser.add_argument("-r","--reload",help="Use flag when reloading existing",action="store_true")
    parser.add_argument("-s","--search",help="Search for articles continaing the given word",default="")
    parser.add_argument("-c","--count",help="Return number of articles found",action="store_true")

    args = parser.parse_args(sys.argv)

    #conect to db
    articles = ArticleManager()
    articles.connect()
    
    #drop table
    if args.reload:
        articles.reload()

    #add table
    if args.load:
       articles.load()

    if len(args.search)>0:
        results = articles.search(args.search,args.count)
        if args.count:
            print results
        else:
            print ' '.join(results)

    #close connection
    articles.disconnect()
