# -*- encoding: utf8 -*-
import numpy as np
import random
from gbrt_conf import *
from sklearn.ensemble import GradientBoostingClassifier

def read_features(file):
	label = []
	x_array = []
	header = []
	no = 0
	start = datetime.now()
	with open(file, "r") as fid:
		for line in fid:
			seg = line.strip().split(" ")
			feature_num = len(seg) - 2
			one_sample = [0.0 for i in range(feature_num)]

			for feature_indx in range(feature_num):
				indx = feature_indx + 2
				fv_pair = seg[indx].split(":")
				if len(fv_pair) == 2:
					feature_name, feature_value = fv_pair
				else:
					# nominal features
					p = seg[indx].split("_")
					feature_name = "_".join(p[:-1])
					feature_value = p[-1]
				if no == 0:
					header.append(feature_name)
				else:
					if header[feature_indx] != feature_name:
						raise Exception("Feature format illegal, different with previous line:\n" + line)
				one_sample[feature_indx] = float(feature_value)
			if no % 10000 == 0:
				print "processed",no,"lines, eclapse time:", datetime.now() - start
			x_array.append(one_sample)
			label.append(int(seg[0]))
			no += 1
	return header, x_array, label

if __name__ == "__main__":
	if load_sample:
		header, x_array, label = load_obj(sample_save_file)
	else:
		header, x_array, label = read_features(feature_file)
		save = [header, x_array, label]
		save_obj(save, sample_save_file)

	random.seed(502227)
	all_sample_num = len(label)
	all_index = range(all_sample_num)
	train_num = int(all_sample_num * 0.7)
	train_index = set(random.sample(all_index, train_num))
	test_index = set(all_index) - set(train_index)
	train_bool = np.asarray([i in train_index for i in all_index])
	test_bool = np.asarray([i in test_index for i in all_index])

	all_sample = np.array(x_array, dtype=np.float32)
	all_label = np.array(label, dtype=np.int)

	train_x = all_sample[train_bool, :]
	train_y = all_label[train_bool]

	test_x = all_sample[test_bool, :]
	test_y = all_label[test_bool]

	if load_model == False:
		clf = GradientBoostingClassifier(n_estimators=tree_num, \
	                                 learning_rate=learning_rate, \
	                                 max_depth=tree_max_depth, \
									 subsample=subsample, \
	                                 min_samples_split=min_samples_split, \
	                                 min_samples_leaf=min_samples_leaf, \
	                                 max_features=feature_ratio,\
	                                 random_state=0)
		clf.fit(train_x, train_y)
		save_obj(clf, model_save_file)
	else:
		clf = load_obj(model_save_file)

	test_predict = clf.predict(test_x)
	with open(test_predict_file, "w") as fid:
		for i, true_label in enumerate(test_y):
			fid.write("%d, %d\n" % (test_predict[i], true_label))

	with open(feature_important_file, "w") as fid:
		for i, feature_name in enumerate(header):
			fid.write("%s, %f\n" % (feature_name, clf.feature_importances_[i]))

	print "gbrt score: ",clf.score(test_x, test_y)
