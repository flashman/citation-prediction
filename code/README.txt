CS4780
Final Project
Submitted on Dec 11, 2013
@authors: Michael Flashman, Hyung Joo Parg, Andrey Gushchin
@netid: mtf53, hp255, avg36

*********************
Description
*********************
Command-line tools, classes, and functions for predicting citation counts on arxiv pre-prints
See details below.

*********************
Dependencies
*********************
All code is written for python2.7 and uses standard libraries. 

    -----------------
    python libraries
    -----------------
    sys
    os
    re
    argparse
    datetime
    pickle
    matplotlib
    scipy
    numpy
    itertools
    subprocess

SVMLight executables (from Thorston Jochims' SVMLight) are required for our custom SVMLight python wrapper.
These should be placed in the lib/ directory. 
    
    -----------------
    svmlight exec
    -----------------
    lib/svm_classify
    lib/svm_learn

*****************************
Data
****************************
Code assumes that data is organized as follows:

	-----------------
	citation network
	-----------------
	The citation network data should be stored as an edge list, with one edge per line.
	For example: 
	    # FromNodeId	ToNodeId
	      0001001	    9304045
	      0001001	    9308122
	      0001001	    9309097
	By default, the files is assued to reside at ../data/cit-hep-th.txt

	------------------
	arxiv document data
	-------------------
	The arxiv document data is stored in a folder (../data/hep-th-svm/ or ../data/hep-th-svm.ta) with one 
	file per year/month, and named accordingly. For example, 0001.svm contains data for documents submitted in Jan 2000.  
	Each file contains a list of document feature vectors in SVMLight format, and are labeled by the document's arxiv id.
	For example:
	    0001001 1:1 3:7 19:1 24:3 35:5 39:6 60:2 87:2 93:1 101:2 108:1 ...
	    0001002 3:1 11:3 343:1 515:1 612:1 636:1 659:1 683:1 880:1 933:1 ...
	Arxiv id's are used down stream to match citation counts to specific articles.
	Each feature corresponds to a 3-gram in the original document. The mapping between feature_id and 3-gram is stored in 
	vocabulary.txt, butis not currently in use.

****************************
Code
****************************
A general description of the various pieces, in order of importance.

---------------------
citationPrediction.py
_____________________
Description: 
General purpose command line tool for all your citation prediction needs.  Runs in 7 different modes. 

Example: 
money-cash$ python citationPrediction.py -root ../data/hep-th-svm/ -ts 9401 -te 9501 -m 24 -tw 24 -svm -3 -s

Usage: 
citationPrediction.py [-h] [-root ROOT] [-citation CITATIONDATA]
                             [-ts TRAINSTART] [-te TRAINEND] [-tw TRAINWINDOW]
                             [-pb PREDICTBUFFER] [-ps PREDICTSTART]
                             [-pe PREDICTEND] [-t CITATIONTHRESHOLD]
                             [-m CITATIONMONTHS] [-svm] [-r] [-ep EPSILON]
                             [-o OPTIONS] [-nb] [-0] [-1] [-2] [-3] [-4] [-5]
                             [-6] [-s]

operating mode arguments:
  -0, --e0              Perform basic classification with given paramters
  -1, --e1              Run experiment with loop over t (citation accumulation
                        windoow) and w (duration of trianing data)
  -2, --e2              Run experiment with loop over seperation distance
                        between training and test data, for fixed test set
  -3, --e3              Run experiment with loop over seperation distance
                        between training and test data, for fixed training set
  -4, --e4              Run experiment with loop over c value for svm
  -5, --e5              Run experument with loop over single months between
                        predict start and predict end
  -6, --e6              Run experument with leave one month out error

classifier mode arguments:
  -svm, --svm           Predict with support vector machine
  -r, --regression      Perform regression based analysis. Only valid for svm
  -ep EPSILON, --epsilon EPSILON
                        Regression tollerence. Only relevent for svm
                        regression
  -o OPTIONS, --options OPTIONS
                        Optional parameter string for SVM classifier. Ignored
                        by naive bayes classifier.
  -nb, --naivebayes     Prediict with naive bayes.

additional classifier and prediction arguments:
  -h, --help            show this help message and exit
  -root ROOT, --root ROOT
                        Root directory of document feature vectors (one file
                        per month)
  -citation CITATIONDATA, --citationData CITATIONDATA
                        Location of citation network data.
  -ts TRAINSTART, --trainstart TRAINSTART
                        Specify start date of training documets. Eg '9501'
  -te TRAINEND, --trainend TRAINEND
                        Specify end date of training documets. Eg '9601'
  -tw TRAINWINDOW, --trainwindow TRAINWINDOW
                        Specify the size of the trainging period. Eg 12
  -pb PREDICTBUFFER, --predictbuffer PREDICTBUFFER
                        Specify the seperation between training and test data.
                        Eg 12
  -ps PREDICTSTART, --predictstart PREDICTSTART
                        Specify start date of prediction documets. Eg '9501'
  -pe PREDICTEND, --predictend PREDICTEND
                        Specify end date of prediction documets. Eg '9601'
  -t CITATIONTHRESHOLD, --citationThreshold CITATIONTHRESHOLD
                        Citation count threshold.
  -m CITATIONMONTHS, --citationMonths CITATIONMONTHS
                        Number of citationMonths used in tabulation of article
                        citations.
  -s, --save            Save results to file (as pickled dict)

---------------------
citationPrediction.py
_____________________
Description: 
General purpose command line tool for all your citation prediction needs.  Runs in 7 different modes. 

Example: 
money-cash$ python citationPrediction.py -root ../data/hep-th-svm/ -ts 9401 -te 9501 -m 24 -tw 24 -svm -3 -s






