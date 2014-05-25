# -*- encoding: utf8 -*-
import os
import numpy as np
from datetime import *
import traceback
import cPickle
import random
from gbrt_conf import *
from sklearn.ensemble import GradientBoostingClassifier
from sklearn import cross_validation, grid_search

header, x_array, label = load_obj(sample_save_file)

random.seed(502227)
all_sample_num = len(label)
all_index = range(all_sample_num)
train_num = int(all_sample_num * 0.9)
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

gbrt = GradientBoostingClassifier()
parameter_grid = {'n_estimators' : np.linspace(10, 130, 5),
                 'learning_rate': np.linspace(0.1, 1, 5),
                 'max_depth' : np.linspace(1,4,4),
                 'feature_ratio' : np.linspace(0.1, 1, 5)}
gbrt_best = grid_search.GridSearchCV(gbrt, parameter_grid, verbose=2)
gbrt_best.fit(train_x, train_y)

save_obj(gbrt_best, "../kaggle/gbrt_best.cpk")