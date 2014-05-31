#!/usr/bin/env python
# -*- encoding: utf8 -*-
import numpy as np
import matplotlib.pyplot as plt

from sklearn.ensemble.partial_dependence import partial_dependence
from gbrt_conf import *
from sklearn import metrics


header, x, y = load_obj("../kaggle/train.cpk")
gbrt = load_obj("../kaggle/gbrt_best.cpk")
print "best prameters:", gbrt.get_params()

sample_x = np.array(x, dtype=np.float32)
sample_y = np.array(y, dtype=np.float32)
train_set, test_set, index = split_train_test(seed, sample_x, sample_y, 0.9)

test_x, test_y = test_set
test_n = test_x.shape[0]

yprob = gbrt.predict_proba(test_x)
precision, recall, thresholds = metrics.precision_recall_curve(test_y, yprob[:,1])
fpr, tpr, th = metrics.roc_curve(test_y, yprob[:,1])
pr_auc = metrics.average_precision_score(test_y, yprob[:,1])
auc = metrics.auc(fpr, tpr)
print "auc:", auc, "pr_auc:",pr_auc

# TODO 具体预测函数？
# th = 0.5
# yproba = gbrt.predict_proba(sample_x)
# for i, x in enumerate(sample_x):
# 	if index[i] == False:
# 		# test sample:


# show top10 important features:
sorted_feature_important_ind = gbrt.feature_importances_.argsort()
with open(feature_important_file, "w") as fid:
	for i in sorted_feature_important_ind:
		fea_name = header[i]
		fea_imp = gbrt.feature_importances_[i]
		fid.write("%s:%f\n" % (fea_name, fea_imp))

# top10_important_feature = sorted_feature_important_ind[-6:]
#
# for i in range(6):
# 	fea_id = top10_important_feature[-1-i]
# 	fea_name = header[fea_id]
# 	print "examing feature ", fea_id, ":", fea_name,\
# 		"[", gbrt.feature_importances_[fea_id],"]"
# 	pd = partial_dependence(gbrt, fea_id, X=test_x, \
#                          grid_resolution=20)
#
# 	plt.subplot(3, 2, i)
# 	plt.ylabel(fea_name)
# 	plt.plot(pd[1][0], pd[0][0], "yo-")
# plt.show()
