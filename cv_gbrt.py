#!/usr/bin/env python
# -*- encoding: utf8 -*-
from gbrt_conf import *
from sklearn.ensemble import GradientBoostingClassifier
from sklearn import grid_search
from scipy.stats import uniform


if __name__ == "__main__":
	if load_sample:
		header, x_array, label = load_obj(sample_save_file)
	else:
		header, x_array, label, _ = read_features(feature_file)
		save = [header, x_array, label]
		save_obj(save, sample_save_file)

	train_set, test_set, _ = split_train_test(seed, x_array, label, 0.9)

	train_x, train_y = train_set
	# print "size of train_x is", train_x.shape

	gbrt = GradientBoostingClassifier()
	parameter_grid = {'n_estimators' : range(10, 110, 10),
	                 'learning_rate': uniform(loc = 0.01, scale = 0.99),
	                 'max_depth' : range(1, 6, 1),
		             'max_features' : uniform(loc = 0.1, scale = 0.89),
		             'subsample' : uniform(loc = 0.2, scale = 0.79),
		             'min_samples_leaf' : [min_samples_leaf],
		             'min_samples_split' : [min_samples_split]}
	gbrt_gridsearch = grid_search.RandomizedSearchCV(gbrt, \
	                parameter_grid, scoring = auc, \
	                cv=4, n_jobs=2, n_iter=100, verbose=5, refit=False)
	gbrt_gridsearch.fit(train_x, train_y)

	gbrt_best = GradientBoostingClassifier(verbose=2, **gbrt_gridsearch.best_params_)
	gbrt_best.fit(train_x, train_y)
	print "parameters:", gbrt_best.get_params()
	save_obj(gbrt_best, model_save_file)