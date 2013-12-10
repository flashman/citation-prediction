import pickle
import matplotlib.pyplot as plt

FN = '../results/binary.ta.svm.rba.9901-0101.2013-12-07.681116.pickle'
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
    baseline = [v['baseline'] for v in results[k]]
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
plt.savefig(SFN)



