import pickle
import matplotlib.pyplot as plt

FN=['']*5
FN[0] = '../results/binary.nb.ta.t5.9901-0101.2013-12-04.365238.pickle'
FN[1] = '../results/binary.nb.ta.t5.b6.9901-0101.2013-12-04.813727.pickle'
FN[2] = '../results/binary.nb.ta.t5.b12.9901-0101.2013-12-04.477422.pickle'
FN[3] = '../results/binary.nb.ta.t5.b24.9901-0101.2013-12-04.912666.pickle'
FN[4] = '../results/binary.nb.ta.t5.b48.9901-0101.2013-12-04.150970.pickle'
B=[0,6,12,24,48]

results=[0]*5
for i, fn in enumerate(FN): 
    f = open(fn,'r')
    results[i] = pickle.load(f)['results']
    f.close()

keys = sorted(results[0].keys())

fig = plt.figure()
for i,k in enumerate(keys):
    ax = plt.subplot(3,3,i+1)
    avgErr = []
    avgBas = []
    avgDif = []
    for j in range(5):
        errors = [v['errorRate'] for v in results[j][k]]
        baseline = [v['naive'] for v in results[j][k]]
        diff = [b-e for b,e in zip(baseline,errors)]
        avgErr.append( [1.0- sum(errors)/len(errors)]*len(errors))
        avgBas.append([1.0 -sum(baseline)/len(errors)]*len(errors))
        avgDif.append( [sum(diff)/len(errors)]*len(errors))
    plt.plot(B,avgErr, 'b', label='Naive Bayes')
    plt.plot(B,avgBas, 'g', label='Majority')
    plt.tight_layout()
#    plt.plot(B,avgDif, 'red')
    ax.set_title('t={0}, w={1}'.format(*k))
    ax.set_ylim([0.4, 1])
fig.text(0.01, 0.5, 'Average accuracy', ha='center', va='center', rotation='vertical')
fig.text(0.5, 0.02, 'Seperation between training and test data (months)', ha='center', va='center')
#plt.show()
plt.savefig('../results/effectsOfTrainAndTestSep.eps')
plt.clf()

fig = plt.figure()
fig.set_size_inches(16,4)
k=(24,24)
ax = plt.subplot(1,1,1)
avgErr = []
avgBas = []
avgDif = []
for j in range(5):
    errors = [v['errorRate'] for v in results[j][k]]
    baseline = [v['naive'] for v in results[j][k]]
    diff = [b-e for b,e in zip(baseline,errors)]
    avgErr.append( [1.0- sum(errors)/len(errors)]*len(errors))
    avgBas.append([1.0 -sum(baseline)/len(errors)]*len(errors))
    avgDif.append( [sum(diff)/len(errors)]*len(errors))
plt.plot(B,avgErr, 'b', label='Naive Bayes')
plt.plot(B,avgBas, 'r', label='Baseline')
plt.xlabel('Seperation distance between training and test data (months)',fontsize='large') 
plt.ylabel('Avg accuracy')
#ax.set_title('t={0}, w={1}'.format(*k))
plt.ylim([0.5, .8])

#plt.title('Naive Bay)
#fig.text(0.01, 0.5, 'Average accuracy', ha='center', va='center', rotation='vertical')
#fig.text(0.5, 0.02, 'Seperation between training and test data (months)', ha='center', va='center')
#plt.show()
plt.savefig('../results/effectsOfTrainAndTestSep.t24.w24..eps',bbox_inches='tight',pad_inches=.2)
