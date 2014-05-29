#!/usr/bin/env python
# -*- encoding: utf8 -*-
from sklearn import cross_validation
from sklearn.ensemble.partial_dependence import partial_dependence
from gbrt_conf import *
import numpy as np
import matplotlib.pyplot as plt
from sklearn import metrics


header, x, y = load_obj("../kaggle/train.cpk")
gbrt = load_obj("../kaggle/gbrt_best.cpk")
print "best prameters:", gbrt.get_params()

sample_x = np.array(x, dtype=np.float32)
sample_y = np.array(y, dtype=np.float32)
train_set, test_set = split_train_test(seed, sample_x, sample_y, 0.9)

test_x, test_y = test_set
class_pred = gbrt.predict(test_x)
print "f1_score:", metrics.f1_score(test_y, class_pred)

yprob = gbrt.predict_proba(test_x)
precision, recall, thresholds = metrics.precision_recall_curve(test_y, yprob[:,1])
pr_auc = metrics.average_precision_score(test_y, yprob[:,1])
print "auc", pr_auc
plt.plot(recall, precision, "b.-")
plt.ylabel("precision")
plt.xlabel("recall")
plt.show()


top10_important_feature = list(gbrt.feature_importances_.argsort()[-10:])

# for fea_id in range(6):
# 	fea_name = header[top10_important_feature[-1-fea_id]]
# 	print "examing feature ", fea_id, ":", fea_name
# 	pd = partial_dependence(gbrt, top10_important_feature[-1-fea_id], X=test_x, \
#                          grid_resolution=20)
#
# 	plt.subplot(3, 2, fea_id+1)
# 	plt.ylabel(fea_name)
# 	plt.plot(pd[1][0], pd[0][0], "yo-")

fea_id = 2
fea_name = header[top10_important_feature[-1-fea_id]]
print "examing feature ", fea_id, ":", fea_name
pd = partial_dependence(gbrt, top10_important_feature[-1-fea_id], X=test_x, \
                     grid_resolution=20)
fea_name = header[top10_important_feature[-1-fea_id]]
plt.ylabel(fea_name)
plt.plot(pd[1][0], pd[0][0], "yo-")
plt.show()
