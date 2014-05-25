# -*- encoding: utf8 -*-
import numpy as np
from datetime import *
import traceback
import cPickle
from ValuedShopper import *

feature_file = "../kaggle/train_features.txt"
def read_features(file):
	label = []
	x_array = []
	header = []
	no = 0
	with open(file, "r") as fid:
		for line in fid:
			seg = line.strip().split(" ")
			feature_num = len(seg) - 2 + 1
			one_sample = [0.0 for i in range(feature_num)]

			for indx in range(2, feature_num):
				feature_indx = indx - 2
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
			x_array.append(one_sample)
			label.append(int(seg[0]))
			no += 1
	return header, x_array, label


def save_obj(obj, file):
	with open(file, "wb") as fid:
		cPickle.dump(obj, fid)


def load_obj(file):
	with open(file) as fid:
		obj = cPickle.load(fid)
	return obj
load = False
save_file = "../kaggle/train.cpk"
if __name__ == "__main__":
	if load:
		header, x_array, label = load_obj(save_file)
	else:
		header, x_array, label = read_features(feature_file)
		save = [header, x_array, label]
		save_obj(save, save_file)

	