# -*- encoding: utf8 -*-
import sys
import os
from datetime import *
import traceback
from ValuedShopper import *

reload(sys)
sys.setdefaultencoding('utf-8')

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

offers = "../kaggle/offers.csv"
test_history = "../kaggle/testHistory.csv"
train_history = "../kaggle/trainHistory.csv"
transactions = "../test_dir/split_out_transactions"
# offers = "test_dir/offers.csv"
# test_history = "../test_dir/testHistory.csv"
# train_history = "../test_dir/trainHistory.csv"
# transactions = "test_dir/transactions.csv"
# features = "test_dir/features_dir"
if __name__ == "__main__":
	# fid = open(transactions)
	# with open("test_dir/transactions.csv", "w") as test_transaction:
	#     for i, line in enumerate(fid):
	#         if i > 300000:
	#             break;
	#         test_transaction.write(line)
	# fid.close()
	# save old version:
	timestamp = datetime.now().isoformat()

	print "begin extracting train file"
	latest_feature = "../kaggle/train_features.txt"
	old_feature = "../kaggle/train_features" + timestamp + ".txt"
	try:
		os.rename(latest_feature, old_feature)
	except Exception:
		print "rename", latest_feature, "to", old_feature,"failed, never mind!"

	extractor_feature(train_history, offers, transactions, latest_feature)

	print "begin extracting test file"
	latest_feature = "../kaggle/test_features.txt"
	old_feature = "../kaggle/test_features" + timestamp + ".txt"
	try:
		os.rename(latest_feature, old_feature)
	except Exception:
		print "rename", latest_feature, "to", old_feature,"failed, never mind!"

	extractor_feature(test_history, offers, transactions, latest_feature)
	pass