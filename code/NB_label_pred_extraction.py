import pickle
import numpy as np

#LOAD PICKLED DICTIONARIES
#ta_dict = pickle.load(open('nb.ta.pickle','r'))
#full_dict =  pickle.load(open('nb.full.pickle','r'))
ta_dict = pickle.load(open('svm.ta.pickle','r'))
full_dict =  pickle.load(open('svm.full.pickle','r'))

#CITATION ACCUMULATION PERIOD AND WINDOW PARAMETERS
cap_param = 24
wind_param = 24
#LENGTH OF PREDICTION PERIOD
ta_num_months = len(ta_dict['results'][(cap_param,wind_param)])
full_num_months = len(full_dict['results'][(cap_param,wind_param)])

for i in xrange(ta_num_months):
    ta_labels = np.array(ta_dict['results'][(cap_param,wind_param)][i]['labels'])
    ta_preds = np.array(ta_dict['results'][(cap_param,wind_param)][i]['predictions'])
    ta_arr = np.transpose(np.vstack((ta_labels,ta_preds)))
    ta_filename = 'svm_pred_label_ta_' + str(i+1) + '.dat'
    np.savetxt(ta_filename,ta_arr, fmt='%i', delimiter=' ')

for i in xrange(full_num_months):
    full_labels = np.array(full_dict['results'][(cap_param,wind_param)][i]['labels'])
    full_preds = np.array(full_dict['results'][(cap_param,wind_param)][i]['predictions'])
    full_arr = np.transpose(np.vstack((full_labels,full_preds)))
    full_filename = 'svm_pred_label_full_' + str(i+1) + '.dat'
    np.savetxt(full_filename,full_arr, fmt='%i', delimiter=' ')




