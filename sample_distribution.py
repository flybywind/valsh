#!/usr/bin/env python
# -*- encoding: utf8 -*-
from gbrt_conf import *


header, x, y = load_obj("../kaggle/train.cpk")
sample_x = np.array(x, dtype=np.float32)
sample_y = np.array(y, dtype=np.float32)

def info(x):
	print " min\t\tmax\t\tavg\t\tstd\t\tmedian\t\t1/4\t\t3/4"
	print " %f\t%f\t%f\t%f\t%f\t%f\t%f" % (
	x.min(), x.max(), x.mean(), x.std(), np.median(x), \
	np.percentile(x, 25), np.percentile(x, 75)
	)
	h, edges = np.histogram(x, 10, density=True)
	print " density:", h*np.diff(edges)
	print " edges:", edges

for i, feature_name in enumerate(header):
	print feature_name,": general"
	x = sample_x[:, i]
	info(x)
	x1 = x[sample_y == 1]
	print feature_name,": positive"
	info(x1)

	x0 = x[sample_y == 0]
	print feature_name,": negative"
	info(x0)

