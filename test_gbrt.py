# -*- encoding: utf8 -*-
import numpy as np
import sklearn.metrics
from gbrt_conf import *


if __name__ == "__main__":
	gbrt_gs = load_obj(grid_search_model_file)
	clf = gbrt_gs.best_estimator_

	header, x_array, label = load_obj(sample_save_file)
	train_set, test_set = split_train_test(502227, x_array, label, 0.9)
	test_x, test_y = test_set

	proba_x = clf.predict_proba(test_x)
	with open(test_predict_file, "w") as fid:
		for i, prob in enumerate(proba_x):
			fid.writ("%d,%f,%f\n" % (test_y[i], proba_x[i][0], proba_x[i][1]))

	with open(feature_important_file, "w") as fid:
		for i, feature_name in enumerate(header):
			fid.write("%s, %f\n" % (feature_name, clf.feature_importances_[i]))

	print ""
	print "gbrt score: ",clf.score(test_x, test_y)