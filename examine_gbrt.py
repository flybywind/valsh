# -*- encoding: utf8 -*-
from sklearn import cross_validation
from sklearn.ensemble.partial_dependence import partial_dependence
from gbrt_conf import *
import numpy as np
header, x, y = load_obj("../kaggle/train.cpk")
gbrt = load_obj("../kaggle/gbrt.cpk")
sample_x = np.array(x, dtype=np.float32)
sample_y = np.array(y, dtype=np.float32)
kf = cross_validation.KFold(len(x), 10)
tr, test_index = kf.__iter__().next()

top10_important_feature = gbrt.feature_importances_.argsort()[-10:]

test_x = sample_x[test_index]
test_y = sample_y[test_index]
# gbrt.fit(test_x, test_y)
pd = partial_dependence(gbrt, X=test_x, target_variables=top10_important_feature[-3:],\
                         grid_resolution=20)
