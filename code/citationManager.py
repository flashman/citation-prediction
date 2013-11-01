'''
@created: Oct 29, 2013
@author: homoflashmanicus
'''

import sys
import psycopg2 as pg
from argparse import ArgumentParser

DB_NAME = 'networks_dev'
USER = 'networks'
PW = 'networks'
HOST = 'localhost'
DATADIR='../data/cit-HepTh.txt'

#UTILITY FUNCTIONS
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

if __name__ == '__main__':
    '''
    The main program
    '''

    #parse inputs
    parser = ArgumentParser()
    parser.add_argument("main")
    parser.add_argument("-l","--load",help="use flag when loading from scratch",action="store_true")
    parser.add_argument("-r","--reload",help="use flag when reloading existing",action="store_true")
    parser.add_argument("-cd","--cited",help="get articles cited by", default='')
    parser.add_argument("-cg","--citing",help="get articles citing", default='')
    args = parser.parse_args(sys.argv)

    #conect to db
    db = pg.connect("dbname=" + DB_NAME + " user=" + USER + " password=" + PW + " host=" + HOST)
    cur = db.cursor()
    
    #drop table
    if args.reload:
        cur.execute("DROP table citation_network")

    #add table
    if args.reload or args.load:
        cur.execute(" CREATE TABLE citation_network (  id serial NOT NULL,source char(7),target char(7), CONSTRAINT citation_network_pkey PRIMARY KEY (id) )")

        #read in citation network data
        f=open(DATADIR)
        raw = f.read()
        f.close()
        
        links = []
        for line in raw.splitlines():
            if line[0] == '#': continue
            papers = [fixID(p) for p in line.split()]
            links.append({'source': papers[0],'target': papers[1]})
        
        #commite citation network to db
        cur.executemany("INSERT INTO citation_network (source, target) VALUES (%(source)s,%(target)s) ", links)

    if len(args.cited)==7:
        cur.execute(" SELECT source from citation_network WHERE target=%s ", (args.cited,))
        results = cur.fetchall()
        print "CITED BY: " + str(len(results)) + " ARTICLES"
        for r in results:
            print r[0]

    if len(args.citing)==7:
        cur.execute(" SELECT target from citation_network WHERE source= %s ", (args.citing,))
        results = cur.fetchall()
        print "CITING: " + str(len(results)) + " ARTICLES"
        for r in results:
            print r[0]


    #save changes and close
    db.commit()
    cur.close()
    db.close()
