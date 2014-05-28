#!/usr/bin/env python
# -*- encoding: utf8 -*-
from sklearn import cross_validation
from sklearn.ensemble.partial_dependence import partial_dependence
from gbrt_conf import *
import numpy as np
import matplotlib.pyplot as plt
header, x, y = load_obj("../kaggle/train.cpk")
gbrt_gs = load_obj("../kaggle/gbrt_best.cpk")
gbrt = gbrt_gs.best_estimator_
print "best prameters:", gbrt_gs.best_params_

sample_x = np.array(x, dtype=np.float32)
sample_y = np.array(y, dtype=np.float32)
kf = cross_validation.KFold(len(x), 10)
tr, test_index = kf.__iter__().next()

top10_important_feature = list(gbrt.feature_importances_.argsort()[-10:])

test_x = sample_x[test_index]
test_y = sample_y[test_index]
# gbrt.fit(test_x, test_y)

for fea_id in range(6):
	fea_name = header[top10_important_feature[-1-fea_id]]
	print "examing feature ", fea_id, ":", fea_name
	pd = partial_dependence(gbrt, top10_important_feature[-1-fea_id], X=test_x, \
                         grid_resolution=20)

	plt.subplot(3, 2, fea_id+1)
	plt.ylabel(fea_name)
	plt.plot(pd[1][0], pd[0][0], "yo-")


plt.show()
