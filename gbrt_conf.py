import os
import traceback
import cPickle
import random
import numpy as np
from sklearn import metrics
from datetime import *

seed = 502227
load_sample = True
load_model = False
feature_file = "../kaggle/train_features.txt"
sample_save_file = "../kaggle/train.cpk"
model_save_file = "../kaggle/gbrt_best.cpk"
grid_search_model_file = "../kaggle/gbrt_best.cpk"
test_predict_file = "../kaggle/test_predict.txt"
feature_important_file = "../kaggle/feature_important.csv"
learning_rate = 0.6
tree_num = 100
# tree_num = 500    # 0.74053479945
subsample = 1.0
min_samples_split = 10
min_samples_leaf = 5
tree_max_depth = 3
feature_ratio = 0.9


def save_obj(obj, file):
	timestamp = datetime.now().isoformat()
	old = file + timestamp
	try:
		os.rename(file, old)
	except Exception as e:
		traceback.print_exc()
		print "WARNING: rename old file failed", e
	with open(file, "wb") as fid:
		cPickle.dump(obj, fid)


def load_obj(file):
	with open(file) as fid:
		obj = cPickle.load(fid)
	return obj


def split_train_test(seed, x_array, label, ratio):
	random.seed(seed)
	all_sample_num = len(label)
	all_index = range(all_sample_num)
	train_num = int(all_sample_num * ratio)
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
	return (train_x, train_y), (test_x, test_y), train_index


def auc(estimator, x, y):
	yprob = estimator.predict_proba(x)
	pr_auc = metrics.average_precision_score(y, yprob[:,1])
	return pr_auc

def f1_score(estimator, x, y):
	yprob = estimator.predict(x)
	# yp = yprob[:,1] > 0.8
	s = metrics.f1_score(y,yprob)
	# print "size of x is", x.shape
	# print "f1 score is", s
	return s


def read_features(file):
	label = []
	x_array = []
	header = []
	id = {}
	no = 0
	start = datetime.now()
	with open(file, "r") as fid:
		for line in fid:
			seg = line.strip().split(" ")
			id[no] = seg[1][1:]
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
	return header, x_array, label, id