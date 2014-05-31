# -*- encoding: utf8 -*-
import sys
from datetime import *
import cPickle
from ValuedShopper import *
reload(sys)
sys.setdefaultencoding('utf-8') 
		
# 使用train和test中的所有customer id为过滤条件。把这批数据过滤出来
# transactions.csv中的数据是顺序存放的
def split_transactions(transactions, split_out_dir):
	start = datetime.now()
	csv_file = open(transactions)
	head = csv_file.next() # head

	line = csv_file.next()
	last_customer_id = line.split(",")[0]
	customer_id_record = {}
	customer_id_record[last_customer_id] = 1 
	customer_file = split_out_dir + "/" + str(last_customer_id) + ".csv"
	fid = open(customer_file, 'w')
	fid.write(head)
	fid.write(line)
	issort = True

	for e, line in enumerate(csv_file):
		seg = line.strip().split(",")
		customer_id = seg[0]
		if last_customer_id != customer_id:
			fid.close()

			customer_file = split_out_dir + "/" + str(customer_id) + ".csv"
			if customer_id in customer_id_record:
				print "rewrite", customer_id
				fid = open(customer_file, 'a')
				issort = False
			else:
				customer_id_record[customer_id] = 1
				fid = open(customer_file, 'w')
				fid.write(head)

			last_customer_id = customer_id

		fid.write(line)

		if e % 50000 == 0:
			print e, datetime.now() - start
			print >> sys.stderr, e, datetime.now() - start
	fid.close()
	print e, datetime.now() - start,"sort:",str(issort)

offers = "kaggle/offers.csv"
test_history = "kaggle/testHistory.csv"
train_history = "kaggle/trainHistory.csv"
transactions = "kaggle/transactions.csv"
features = "kaggle/features_dir"
split_out_dir = "test_dir/split_out_transactions"
# offers = "test_dir/offers.csv"
# test_history = "test_dir/testHistory.csv"
# train_history = "test_dir/trainHistory.csv"
# transactions = "test_dir/transactions.csv"
# features = "test_dir/features_dir"
# split_out_dir = "kaggle/split_out_transactions"
if __name__ == "__main__":
	# fid = open(transactions)
	# with open("test_dir/transactions.csv", "w") as test_transaction:
	# 	for i, line in enumerate(fid):
	# 		if i > 300000:
	# 			break;
	# 		test_transaction.write(line)
	# fid.close()		
	split_transactions(transactions, split_out_dir)
	
	pass