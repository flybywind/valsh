# -*- encoding: utf8 -*-
import sys
import os
from datetime import *
import cPickle
import traceback
from ValuedShopper import *

reload(sys)
sys.setdefaultencoding('utf-8')
def save_obj(obj, file):
	with open(file, "wb") as fid:
		cPickle.dump(obj, fid)

def load_obj(file):
	with open(file) as fid:
		obj = cPickle.load(fid)
	return obj
# transactions.csv中的数据是顺序存放的
def extractor_feature(history_file, offers, transactions_dir, extractor_feature_file):
	start = datetime.now()
	#get all categories on offer in a dict
	offer_map = dict()
	csv_file = CSV(offers)
	for line in csv_file:
		offer_map[line[0]] = Offer(line)

	csv_file = CSV(history_file)
	history_map = {}
	for line in csv_file:
		history_map[line[0]] = OfferHistory(line)
	with open(extractor_feature_file, "w") as out_feature:
		proc = 0
		for customer_id, offer_history in history_map.items():
			cur_offer = offer_map[offer_history.offer]
			customer_file = transactions_dir + "/" + customer_id + ".csv"
			feature = CustomerOfferFeature(customer_file, offer_history, cur_offer)
			try:
				feature.get()
				out_feature.write(str(feature) + "\n")
			except Exception as e:
				print >>sys.stderr, "Error when processing customer:", customer_id, \
						"offer brand:", cur_offer.brand, "offer company:", cur_offer.company
				traceback.print_exc()
				sys.exit(-1)

			proc += 1
			if proc % 1000 == 0:
				print "processed: ", proc, "\neclapse time:", datetime.now() - start
	print "eclapse time:", datetime.now() - start

base_dir = "../kaggle/"
offers = base_dir + "offers.csv"
test_history = base_dir + "testHistory.csv"
train_history = base_dir + "trainHistory.csv"
transactions = "../test_dir/split_out_transactions"

if __name__ == "__main__":
	# save old version:
	t = datetime.now()
	timestamp = "%d-%d-%d_%d-%d-%d" % (t.year, t.month, t.day, t.hour, t.minute, t.second)
	print "begin extracting train file"
	latest_feature = base_dir + "train_features.txt"
	old_feature = base_dir + "train_features" + timestamp + ".txt"
	try:
		os.rename(latest_feature, old_feature)
	except Exception:
		print "rename", latest_feature, "to", old_feature,"failed, never mind!"

	extractor_feature(train_history, offers, transactions, latest_feature)

	save_obj(CustomerOfferFeature.__offer__, base_dir + "offer.map")
	save_obj(CustomerOfferFeature.__category__, base_dir + "category.map")
	save_obj(CustomerOfferFeature.__brand__, base_dir + "brand.map")
	save_obj(CustomerOfferFeature.__company__, base_dir + "company.map")
	save_obj(CustomerOfferFeature.__chain__, base_dir + "chain.map")
	save_obj(CustomerOfferFeature.__dept__, base_dir + "dept.map")

	print "begin extracting test file"
	latest_feature = base_dir + "test_features.txt"
	old_feature = base_dir + "test_features" + timestamp + ".txt"
	try:
		os.rename(latest_feature, old_feature)
	except Exception:
		print "rename", latest_feature, "to", old_feature,"failed, never mind!"

	extractor_feature(test_history, offers, transactions, latest_feature)
	pass