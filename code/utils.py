'''
@created: Nov 1, 2013
@author: homoflashmanicus
@description: utility functions
'''

import re

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

