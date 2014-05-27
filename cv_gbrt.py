# -*- encoding: utf8 -*-
from gbrt_conf import *
from sklearn.ensemble import GradientBoostingClassifier
from sklearn import grid_search
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

	train_set, test_set = split_train_test(502227, x_array, label, 0.9)

	train_x, train_y = train_set

	gbrt = GradientBoostingClassifier()
	parameter_grid = {'n_estimators' : range(10, 110, 30),
	                 'learning_rate': np.linspace(0.1, 1, 5),
	                 'max_depth' : range(1, 5),
	                 'max_features' : np.linspace(0.1, 1, 5)}
	gbrt_best = grid_search.GridSearchCV(gbrt, parameter_grid, cv=2, n_jobs=2, verbose=5)
	gbrt_best.fit(train_x, train_y)

	save_obj(gbrt_best, "../kaggle/gbrt_best.cpk")