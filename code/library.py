'''
CS4780
Problem Set 1
Problem 3a: Book recommendation and classification
Created on Sep 10, 2013
@author: homoflashmanicus
@netid: mtf53
'''

from math import sqrt
from array import array
import numpy as np

class Library:
    '''
    This class manages book titles.
    '''

    def __init__(self, titleFile):
        '''
        Constructor.  Load titles.
        '''
        self.__load__(titleFile)
    
    def __load__(self, data):
        '''
        Load data and return data objects
        ''' 
        #create local variables for efficiency
        title=list()
        titleIndex=dict()
        
        #load data into memory
        f=open(data)
        raw = f.read()
        f.close()
        
        #parse training instances
        idx=0
        for line in raw.splitlines():
            line = line.split('-')
            title.append(line[1])
            if len(line[1])>0:
                titleIndex[line[1]]=idx
            idx += 1
        self.titles = title
        self.indices = titleIndex
