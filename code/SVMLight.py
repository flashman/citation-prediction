'''
SVMLight
@author homoflashmanicus
@netid mtf53
@created Sep 20, 2013
'''

import subprocess as sbp
import os
import utils

class Model:
    ''' SVM light model class.  For now it justs removes model file when we are done'''  
    def __init__(self,modelFile):
        '''
        Parse model
        '''
        self.modelFile = modelFile

    def __del__(self):
        os.remove(self.modelFile)

def learn(trainingData, options=None):
    '''
    Train svm model on data.
    training data is any object whith that saves to svm light format:
        eg. trainingData.save('tmp.svm') 
    Options is command line type string of options for svm_learn executable
    Returns model object.
    '''
    dataFile='train.'+str(utils.current_micro_time())  #tmp file for training data
    modelFile='model.'+str(utils.current_micro_time()) #tmp dile for resulting model

    #create tmp data file for svm_learn executable
    trainingData.save(dataFile)
    
    #build procees and exacute
    process = ['lib/svm_learn']
    if options != None:
        process.extend(options.split())
    process.extend([dataFile,modelFile])
    proc = sbp.Popen(process)
    proc.wait()

    #clean up temp files
    os.remove(dataFile)

    #return model
    return Model(modelFile)

def classify(testData,model,options=None):
    '''
    Classify SVM data using SVM model.
    TestData can be any object that can be saved to svmLight formatted data
    Options is command line type string of options for svm_classify executable
    Returns prediction for each line of testData.
    '''
    testFile='test.'+str(utils.current_micro_time())
    classificationFile='classification.'+str(utils.current_micro_time())
    
    #create tmp data file for classification
    testData.save(testFile)

    #build procees and exacute
    process = ['lib/svm_classify']
    if options != None:
        process.extend(options.split())
    process.extend([testFile, model.modelFile, classificationFile])
    proc = sbp.Popen(process)
    proc.wait()
   
    #read in classificaiton results
    f = open(classificationFile)
    classifications = [float(l) for l in f.read().splitlines()]
    f.close()

    #clean up temp files
    os.remove(testFile)
    os.remove(classificationFile)
    
    return classifications

def multiclassLearn(trainingData,classLabels,options=None):
    #train svm model on each class label
    models = []
    for l in classLabels:
        trainingData.labelForSVM(l)
        m = learn(trainingData,options=options)
        models.append(m)
    return models

def multiclassClassify(testData,models,options=None):
    #classify 
    margin = [-10000.0]*len(testData)
    label = [0]*len(testData)
    for l,m in enumerate(models):
        newMargin = classify(testData,m)
        for i in range(len(margin)):
            if newMargin[i]>margin[i]:
                margin[i] = newMargin[i]
                label[i]=l+1
    return label       
