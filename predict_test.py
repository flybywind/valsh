#!/usr/bin/env python
# -*- encoding: utf8 -*-
from gbrt_conf import *
from sklearn.ensemble import GradientBoostingClassifier

test_file = "../kaggle/test_features.txt"
test_feature = "../kaggle/test_features.cpk"
retrained_model_file = "../kaggle/gbrt.retrain.cpk"
retrain_model = False
load_test = True

if load_test:
	print "load test feature:"
	header, x, y, id = load_obj(test_feature)
else:
	print "parse test file to feature and save:"
	header, x, y, id = read_features(test_file)
	save = [header, x, y, id]
	save_obj(save, test_feature)

test_x = np.array(x, dtype=np.float32)
test_y = np.array(y, dtype=np.float32)

if retrain_model:
	print "retrain model"
	header, x, y = load_obj(sample_save_file)
	sample_x = np.array(x, dtype=np.float32)
	sample_y = np.array(y, dtype=np.float32)
	gbrt_orig = load_obj(model_save_file)
	params = gbrt_orig.get_params()
	params["verbose"] = 3
	gbrt = GradientBoostingClassifier(**params)
	gbrt.fit(sample_x, sample_y)
	save_obj(gbrt, retrained_model_file)
else:
	print "load model"
	gbrt = load_obj(retrained_model_file)

print "predicting"

yprob = gbrt.predict_proba(test_x)
print "id,repeaterprobability"
for i, prob in enumerate(yprob):
	customer_id = id[i]
	print "%s,%f" % (customer_id, prob[1])