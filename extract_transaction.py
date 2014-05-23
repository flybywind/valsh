# -*- encoding: utf8 -*-
import sys
import time
import MySQLdb;
reload(sys) 
sys.setdefaultencoding('utf-8') 

class CSV(object):
 	"""docstring for CSV"""
 	def __init__(self, arg, ishead=True):
 		super(CSV, self).__init__()
 		self.path = arg
 		self.head = None
 		try:
 			self.fid = open(self.path)
 			if ishead:
 				head_str = self.fid.next().strip()
 				self.head = head_str.split(",")
 		except Exception as e:
 			raise e

 	def __iter__(self):
 		return self;
 	
 	def next(self):
 		try:
 			line = self.fid.next().strip()
 			return line.split(",")
 		except Exception as e:
 			self.fid.close()
 			raise e
class Offer(object):
	"""docstring for Offer"""
	def __init__(self, arg):
		super(Offer, self).__init__()
		if len(arg) == 6:
			self.category = int(arg[1])
			self.quantity = int(arg[2])
			self.company = int(arg[3])
			self.offervalue = float(arg[4])
			self.brand = int(arg[5])
		else:
			raise Exception("need 6 field in arg:\noffer,category,quantity,company,offervalue,brand")


if __name__ == "__main__":
	# 打开数据库连接
	table_name = "valued_shopper"
	db = MySQLdb.connect(host = "127.0.0.1",
						 user = "root",
						 db = table_name,
						 charset='utf8')

	# 使用cursor()方法获取操作游标 
	cursor = db.cursor()
	csv_file = CSV("D:\\myproject\\ValuedShopper\\trainHistory.csv")
	# print csv_file.head
	train_history_map = dict()
	offer_map = dict()
	# line = csv_file.next()
	# train_history_map[line[0]] = TransactionHistory(line)
	# print "id = ", line[0],"value = ", str(train_history_map[line[0]])
	# line = csv_file.next()
	# train_history_map[line[0]] = TransactionHistory(line)
	# print "id = ", line[0],"value = ", str(train_history_map[line[0]])
	for line in csv_file:
	# 	print line
		train_history_map[line[0]] = TransactionHistory(line)
	csv_file = CSV("D:\\myproject\\ValuedShopper\\offers.csv")	
	for line in csv_file:
		offer_map[line[0]] = Offer(line)
		
	for customer, history in train_history_map.items():
		sql = "select * from " + table_name + "where customer_id = " + customer \
				+ " and " + " "
		