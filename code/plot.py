import pickle
import matplotlib.pyplot as plt

#FN = '../results/binary.nb.full.t5.9901-0101.2013-12-04.pickle'
#FN = '../results/binary.nb.ta.t5.9901-0101.2013-12-04.365238.pickle'
#FN = '../results/binary.svm.ta.t5.9901-0101.2013-12-04.917038.pickle'
#FN = '../results/binary.nb.ta.t5.b24.9901-0101.2013-12-04.912666.pickle'
#FN = '../results/binary.nb.ta.t5.b12.9901-0101.2013-12-04.477422.pickle'
#FN = '../results/binary.nb.ta.t5.b6.9901-0101.2013-12-04.813727.pickle'
#FN = '../results/binary.svm.full.t5.9901-0101.2013-12-05.241398.pickle'
FN = '../results/binary.nb.ta.t3.9901-0101.2013-12.583809.pickle'

SFN = FN.replace('.pickle','.eps')

f = open(FN,'r')
data = pickle.load(f)
f.close()

print data['metadata']
results = data['results']
keys = sorted(results.keys())

plt.figure()
for i,k in enumerate(keys):
    ax = plt.subplot(3,3,i+1)
    errors = [v['errorRate'] for v in results[k]]
    baseline = [v['naive'] for v in results[k]]
    diff = [b-e for b,e in zip(baseline,errors)]
    avg = [sum(errors)/len(errors)]*len(errors)
    bavg = [sum(baseline)/len(errors)]*len(errors)
    davg = [sum(diff)/len(errors)]*len(errors)
    yymm = [v['predictstart'] for v in results[k]]
    plt.plot(errors, 'k')
    plt.plot(baseline, 'grey')
    plt.plot(diff, 'r')
    plt.plot(avg,'k--')
    plt.plot(bavg,'--', color='grey')
    plt.plot(davg,'--', color='red')
    ax.set_title('t={0},w={1}'.format(*k))
plt.tight_layout()
#plt.show()
plt.savefig(SFN)



