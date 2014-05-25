import os
import traceback
import cPickle
from datetime import *

load_sample = True
load_model = False
feature_file = "../kaggle/train_features.txt"
sample_save_file = "../kaggle/train.cpk"
model_save_file = "../kaggle/gbrt.cpk"
test_predict_file = "../kaggle/test_predict.txt"
feature_important_file = "../kaggle/feature_important.csv"
learning_rate = 0.6
tree_num = 100
# tree_num = 500    # 0.74053479945
subsample = 1.0
min_samples_split = 2
min_samples_leaf = 1
tree_max_depth = 3
feature_ratio = 0.9


def save_obj(obj, file):
	timestamp = datetime.now().isoformat()
	old = file + timestamp
	try:
		os.rename(file, old)
	except Exception as e:
		traceback.print_exc()
		print "WARNING: rename old file failed", e
	with open(file, "wb") as fid:
		cPickle.dump(obj, fid)


def load_obj(file):
	with open(file) as fid:
		obj = cPickle.load(fid)
	return obj

