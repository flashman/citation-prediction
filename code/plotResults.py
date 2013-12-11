from argparse import ArgumentParser
import sys
import pickle
import matplotlib.pyplot as plt

def rSquared(labels,predictions):
    '''Compte r^2 value for predictions given labels'''
    avg = 1.0*sum(labels)/len(labels)
    num = sum( (p - avg)**2 for p in predictions)
    denom = sum((l - avg)**2 for l in labels )
    return num/denom

def plotCAPvsWindowSize(results,title,saveas):

    keys = sorted(results.keys())
    months = [v['predictstart'] for v in results[(6,6)] ]
    months = [ m[0:2]+'/'+m[2:4] for m in months ]
    monthIdx = range(0,len(months))
    print keys
    
    fig = plt.figure()
    fig.set_size_inches(10,8)
    for i,k in enumerate(keys):

        ax = plt.subplot(4,4,i+1)
        errors = [1.0-v['errorRate'] for v in results[k]]
        baseline = [1.0- v['naive'] for v in results[k]]
        avg = [sum(errors)/len(errors)]*len(errors)
        bavg = [sum(baseline)/len(errors)]*len(errors)

        ax.plot(monthIdx, errors, 'k')
        ax.plot(monthIdx, baseline, 'grey')
        ax.plot(monthIdx, avg,'k--')
        ax.plot(monthIdx, bavg,'--', color='grey')
        ax.set_title('t={0},w={1}'.format(*k))
        ax.set_ylim([0.4,0.9])
        plt.xticks(monthIdx[2::6], months[2::6], fontsize=10)
        plt.tight_layout()
    fig.text(0.01, 0.5, 'Accuracy', ha='center', va='center', rotation='vertical')
    fig.text(0.5, 0.01, 'Test Set Month', ha='center', va='center')
    fig.text(0.5,0.99, title, ha='center', va='center')

    if saveas:
        plt.savefig(saveas)
    else:
        plt.show()

def plotTrainTestSep(results,title,saveas):

    keys = sorted(results.keys())
    B = [int(k) for k in keys]

    avgErr = []
    avgBas = []

    for j in keys:
        errors = [v['errorRate'] for v in results[j]]
        baseline = [v['naive'] for v in results[j]]
        avgErr.append( 1.0- sum(errors)/len(errors) )
        avgBas.append(1.0 -sum(baseline)/len(errors) )
    plt.plot(B,avgErr, 'k', label="Naive Bayes")
    plt.plot(B,avgBas, '--', color='grey', label="Baseline")
    plt.xlabel('Seperation between training data and test data (months)') 
    plt.ylabel('Avg accuracy')
    plt.title(title)
    plt.legend()

    if saveas:
        plt.savefig(saveas,bbox_inches='tight',pad_inches=.2)
    else:
        plt.show()

def plotTrainTestSepAll(title,saveas):

    f1 = open('../results/binary.nb.full.ex3.pickle','r')
    f2 = open('../results/binary.nb.ta.ex3.pickle','r')
    f3 = open('../results/binary.svm.ta.ex3.pickle','r')
    f4 = open('../results/binary.svm.full.ex3.pickle','r')
    results1 = pickle.load(f1)['results']
    results2 = pickle.load(f2)['results']
    results3 = pickle.load(f3)['results']
    results4 = pickle.load(f4)['results']
    f1.close()
    f2.close()
    f3.close()
    f4.close()

    keys = sorted(results1.keys())
    B = [int(k) for k in keys]

    avgErr1 = []
    avgErr2 = []
    avgErr3 = []
    avgErr4 = []
    avgBas1 = []
    avgBas2 = []
    avgBas3 = []
    avgBas4 = []

    for j in keys:
        errors1 = [v['errorRate'] for v in results1[j]]
        errors2 = [v['errorRate'] for v in results2[j]]
        errors3 = [v['errorRate'] for v in results3[j]]
        errors4 = [v['errorRate'] for v in results4[j]]
        baseline1 = [v['naive'] for v in results1[j]]
        baseline2 = [v['naive'] for v in results2[j]]
        baseline3 = [v['naive'] for v in results3[j]]
        baseline4 = [v['naive'] for v in results4[j]]
        avgErr1.append( 1.0- sum(errors1)/len(errors1) )
        avgErr2.append( 1.0- sum(errors2)/len(errors2) )
        avgErr3.append( 1.0- sum(errors3)/len(errors3) )
        avgErr4.append( 1.0- sum(errors4)/len(errors4) )
        avgBas1.append(1.0 -sum(baseline1)/len(errors1) )
        avgBas2.append(1.0 -sum(baseline2)/len(errors2) )
        avgBas3.append(1.0 -sum(baseline3)/len(errors3) )
        avgBas4.append(1.0 -sum(baseline4)/len(errors4) )
    plt.plot(B,avgErr1, 'm',  label="NB (Full Text)")
    plt.plot(B,avgErr2, 'g', label="NB (Title/Abstract)")
    plt.plot(B,avgErr3, 'b', label="SVM (Title/Abstract)")    
    plt.plot(B,avgErr4, 'r', label="SVM (Full Text)")    
    plt.plot(B,avgBas1, '--', color='grey', label="Baseline")

    print B
    print avgErr1
    print avgErr2
    print avgErr3
    print avgErr4
    print avgBas1
    plt.xlabel('Training  and test data seperation (months)') 
    plt.ylabel('Average accuracy')
    plt.title(title)
    plt.legend()
    plt.ylim([0.5, .8])

    if saveas:
        plt.savefig(saveas,bbox_inches='tight',pad_inches=.2)
    else:
        plt.show()

def plotRegression(results,title,saveas):
    fig = plt.figure()
    fig.set_size_inches(8,4)
    allLabels = []
    allPredictions = []
    for v in results:
        allLabels.extend( v['labels'] )
        allPredictions.extend( v['predictions'] )
    rsq = rSquared(allLabels,allPredictions)
    plt.scatter(allLabels,allPredictions, color='k', marker='.')
    plt.plot([x for x in range(100)], [y for y in range(100)], 'k--')
    plt.ylim([0,25])
    plt.xlim([0,150])
    plt.xlabel('True citation counts')
    plt.ylabel('Predicted citation counts')
    plt.title('True vs predicted citation counts with SVR with Title/Abstract')
    plt.text(120,22, 'R^2={0:.4f}'.format(rsq),  size=15)
    plt.tight_layout()

    if saveas:
        plt.savefig(saveas,bbox_inches='tight',pad_inches=.2)
    else:
        plt.show()

def plotExperiment4(results,title,saveas):

    #compute average error rates  for difference c values 
    keys = sorted(results.keys())
    avgErr = []
    for j in keys:
        errors = [ v['errorRate'] for v in results[j] ]
        avgErr.append( 1.0- sum(errors)/len(errors) )
    plt.figure()
    plt.plot(keys,avgErr, 'k' , label='SVM with C-value')
    #plt.plot(23.846254166666668, 0.7111975028322917, 'ro', label = 'SVM with default C-value' )  #title abstract
    plt.plot(664.3, .7644, 'ro', label = 'SVM with default C-value' )  #full text

    plt.xlabel('C')
    plt.ylabel('Avgerage Accuracy')
    plt.title(title)
    plt.legend(loc=2)

    if saveas:
        plt.savefig(saveas,bbox_inches='tight',pad_inches=.2)
    else:
        plt.show()
    

if __name__ == '__main__':
    '''
    The main program
    '''
    #parse inputs
    parser = ArgumentParser()
    parser.add_argument("main")
    parser.add_argument("filename",help="location of data to be plotted")
    parser.add_argument("-t", "--type", help="Specify plotting mode. Corresponds to operating modes in citationPredicition.py, more or less.",type=int)
    parser.add_argument("-s","--save", help="save results to file",action="store_true",default=False)
    parser.add_argument("-i","--inspect", help="Inspect metadata", action="store_true")
    parser.add_argument("--title", help="Add a specific title to the figure",type=str, default='')
    parser.add_argument("--saveas", help="Save figure as...", type=str, default=None)


    args = parser.parse_args(sys.argv)

    f = open(args.filename,'r')
    data = pickle.load(f)
    meta = data['metadata']
    results = data['results']
    f.close()

    if args.save and not args.saveas:
        args.saveas = args.filename.replace('.pickle','.eps')
    if args.inspect:
        print meta
    if args.type==1:
        plotCAPvsWindowSize(results,args.title,args.saveas)
    if args.type==2:
        plotTrainTestSep(results,args.title, args.saveas)
    if args.type==3:
        plotRegression(results,args.title,args.saveas)
    if args.type==4:
        plotExperiment4(results,args.title,args.saveas)
    if args.type==5:
        plotTrainTestSepAll(args.title,args.saveas)
