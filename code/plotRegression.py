import pickle
import matplotlib.pyplot as plt

def rSquared(labels,predictions):
    '''Compte r^2 value for predictions given labels'''
    avg = 1.0*sum(labels)/len(labels)
    num = sum( (p - avg)**2 for p in predictions)
    denom = sum((l - avg)**2 for l in labels )
    return num/denom


FN = '../results/regression.full.e1.9901-0101.2013-12-05.523862.pickle'
FN = '../results/regression.ta.e1.9901-0101.2013-12-04.223271.pickle'
FN = '../results/regression.svm.full.9901-9903.2013-12-08_23-43-25.981831.pickle'

SFN = FN.replace('.pickle','.eps')
SFN2 = FN.replace('.pickle','.scatter.eps')

f = open(FN,'r')
data = pickle.load(f)
f.close()

print 'PLOTTING FOR'
print data['metadata']

results = data['results']
keys = sorted(results.keys())

plt.figure()
for i,k in enumerate(keys):
    ax = plt.subplot(3,3,i+1)
    rsq = [rSquared(v['labels'],v['predictions']) for v in results[k]]
    rsqavg = [sum(rsq)/len(rsq)]*len(rsq)
    plt.plot(rsq, 'r')
    plt.plot(rsqavg,'r--')

#    plt.plot(bavg,'--', color='grey')
#    plt.plot(davg,'--', color='red')
    ax.set_title('t={0},w={1}'.format(*k))
plt.tight_layout()
#plt.show()
plt.savefig(SFN)
plt.clf()

plt.figure()
#for i,k in enumerate(keys):
k=(24,24)
ax = plt.subplot(111)
allLabels = []
allPredictions = []
for v in results[k]:
    allLabels.extend( v['labels'])
    allPredictions.extend( v['predictions'])
plt.scatter(allLabels,allPredictions, color='k', marker='.')
plt.plot([x for x in range(100)], [y for y in range(100)], 'k--')
ax.set_ylim([0,50])
ax.set_xlim([0,100])
ax.set_title('t={0},w={1}'.format(*k))
ax.set_xlabel('True citation counts')
ax.set_ylabel('Predicted citation counts')
plt.tight_layout()
#plt.show()
plt.savefig(SFN2)
plt.clf()


