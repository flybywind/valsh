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

		# csv_file = CSV(transactions)

		# line = csv_file.next()
		# last_customer_id = line[0]
		# if last_customer_id in train_customer_id:
		#     customer_history_feature = CustomerHistoryFeature(True)
		# else:
		#     customer_history_feature = CustomerHistoryFeature(False)
		# customer_history_feature.update(line)

		# customer_id_record = {}
		# customer_id_record[last_customer_id] = 1
		# issort = True

		# for e, line in enumerate(csv_file):
		#     customer_id = line[0]
		#     if last_customer_id != customer_id:
		#     # 保存，pickle序列化：
		#         customer_file = extractor_feature_dir + "/" + str(last_customer_id)
		#         with open(customer_file, "wb") as fid:
		#             cPickle.dump(customer_history_feature, fid, 2)

		#         last_customer_id = customer_id
		#         # 已经存在的要重新读出来
		#         if customer_id in customer_id_record:
		#             issort = False
		#             customer_file = extractor_feature_dir + "/" + str(customer_id)
		#             with open(customer_file, "rb") as fid:
		#                 print "reload",customer_id
		#                 customer_history_feature = cPickle.load(fid)
		#         else:
		#             customer_id_record[customer_id] = 1
		#             if customer_id in train_customer_id:
		#                 customer_history_feature = CustomerHistoryFeature(True)
		#             else:
		#                 customer_history_feature = CustomerHistoryFeature(False)


		#     customer_history_feature.update(line)

		# if e % 50000 == 0:
		#     print >> sys.stderr, e, datetime.now() - start

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