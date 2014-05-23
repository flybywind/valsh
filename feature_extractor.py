# -*- encoding: utf8 -*-
import sys
from datetime import *
# import cPickle
from ValuedShopper import *

reload(sys)
sys.setdefaultencoding('utf-8')

# 使用train和test中的所有customer id为过滤条件。把这批数据过滤出来
# transactions.csv中的数据是顺序存放的

def extractor_feature(history_file, offers, istrain, transactions_dir, extractor_feature_file):
	start = datetime.now()
	#get all categories on offer in a dict
	offer_map = dict()
	csv_file = CSV(offers)
	for line in csv_file:
		offer_map[line[0]] = Offer(line)

	csv_file = CSV(history_file)
	history_map = {}
	for line in csv_file:
		history_map[line[0]] = OfferHistory(line, istrain)
	with open(extractor_feature_file, "w") as out_feature:
		for customer_id, offer_history in history_map.items():
			cur_offer = offer_map[offer_history.offer]
			customer_file = transactions_dir + "/" + customer_id
			feature = CustomerOfferFeature(customer_file, offer_history, cur_offer)
			feature.get()
			out_feature.write(str(feature) + "\n")
			print feature
	print "eclapse time:", datetime.now() - start


offers = "../kaggle/offers.csv"
test_history = "../kaggle/testHistory.csv"
train_history = "../kaggle/trainHistory.csv"
transactions = "../test_dir/split_out_transactions"
# offers = "test_dir/offers.csv"
# test_history = "test_dir/testHistory.csv"
# train_history = "test_dir/trainHistory.csv"
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
	extractor_feature(train_history, offers, True, transactions, "../kaggle/train_features")

	pass