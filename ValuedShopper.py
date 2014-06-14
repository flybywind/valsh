# -*- encoding: utf8 -*-
import sys
import StringIO
from datetime import *

reload(sys)
sys.setdefaultencoding('utf-8')

# train_base_date = date(2013, 5, 1).toordinal()
# test_base_date = date(2014, 1, 1).toordinal()


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
			# id category brand都用字符串形式
			self.offer_id = arg[0]
			self.category = arg[1]
			self.quantity = int(arg[2])
			self.company = arg[3]
			self.offervalue = float(arg[4])
			self.brand = arg[5]
		else:
			raise Exception("need 6 field in Offer:\noffer,category,quantity,company,offervalue,brand")


class Transactions(object):
	"""docstring for Transactions"""

	def __init__(self, history_line, base_date):
		super(Transactions, self).__init__()

		if len(history_line) == 11:
			self.customer_id = history_line[0]
			self.chain = history_line[1]
			self.dept = history_line[2]
			self.category = history_line[3]
			self.company = history_line[4]
			self.brand = history_line[5]
			record_date = [int(i) for i in history_line[6].split("-")]
			record_day = date(record_date[0], record_date[1], record_date[2])
			# 距离base date的天数
			self.date_distance = base_date.toordinal() - record_day.toordinal()
			self.productsize = float(history_line[7])
			self.purchasequantity = int(history_line[9])
			self.purchase_dollar = float(history_line[10])
		else:
			raise Exception("need 11 fields in Transactions")


class OfferHistory(object):
	"""docstring for OfferHistory"""

	def __init__(self, arg):
		super(OfferHistory, self).__init__()
		self.arg = arg
		if len(arg) == 7:
			self.customer_id = arg[0]
			self.chain = arg[1]
			self.offer = arg[2]
			self.market = arg[3]
			self.repeattrips = int(arg[4])
			self.repeater = self.repeattrips > 0
			time_ary = [int(i) for i in arg[6].split('-')]
			self.offerdate = date(time_ary[0], time_ary[1], time_ary[2])
		elif len(arg) == 5:
			self.customer_id = arg[0]
			self.chain = arg[1]
			self.offer = arg[2]
			self.market = arg[3]
			self.repeattrips = 0
			self.repeater = False
			time_ary = [int(i) for i in arg[4].split('-')]
			self.offerdate = date(time_ary[0], time_ary[1], time_ary[2])
		else:
			raise Exception(
				"need 7 field in arg:\n'id', 'chain', 'offer', 'market', 'repeattrips', 'repeater', 'offerdate'")

	def __str__(self):
		return "\nchain:%d\noffer:%d\nmarket:%d\nrepeattrips:%d\nofferdate:%s" % \
		       (self.chain, self.offer, self.market, self.repeattrips, time.ctime(self.offerdate))


class CustomerOfferFeature(object):
	"""docstring for Features
	提取新的特征，形式为：
	category_id_amount: amount
	category_id_dollar: dollar
	category_id_time:   time
	....
	one_year_cost:  dollar
	similar_customer_buy:  ratio
	time类型的变量计算方法：按照时间权重计算freq之和
	30天以内的权重0.5,30--60天的权重0.3,60--120天的权重0.2,120天之前的权重0.1
	similar_customer_buy是根据以上特征归一化后算出来的topN用户里面，购买的比例
	这里完全不用时间信息了
	"""
	__category__ = {"key_map":{}, "cnt":0}
	__dept__ = {"key_map":{}, "cnt":0}
	__company__ = {"key_map":{}, "cnt":0}
	__brand__ = {"key_map":{}, "cnt":0}
	__chain__ = {"key_map":{}, "cnt":0}
	__offer__ = {"key_map":{}, "cnt":0}
	def __init__(self, customer_file, offer_history, offer_info):
		super(CustomerOfferFeature, self).__init__()

		self.brand_amount = {}
		self.brand_dollar = {}
		self.brand_time = {}
		self.category_amount = {}
		self.category_dollar = {}
		self.category_time = {}
		self.chain_time = {}
		self.company_amount = {}
		self.company_dollar = {}
		self.company_time = {}
		self.dept_amount = {}
		self.dept_dollar = {}
		self.dept_time = {}
		self.dict_feature = set(self.__dict__.keys())
		self.one_year_shopping_dollar = 0
		self.one_year_shopping_time = 0
		self.float_feature = set(self.__dict__.keys()) - \
				(self.dict_feature.union(set(["dict_feature"])))

		self.customer_info = CSV(customer_file)
		self.offer_history = offer_history
		self.offer_info = offer_info
		# just update dict
		self.getid(offer_info.offer_id, CustomerOfferFeature.__offer__)
		self.getid(offer_info.brand, CustomerOfferFeature.__brand__)
		self.getid(offer_info.company, CustomerOfferFeature.__company__)
		self.getid(offer_info.category, CustomerOfferFeature.__category__)

	def get(self):
		for line in self.customer_info:
			transactions_history = Transactions(line, self.offer_history.offerdate)
			brand_id = self.getid(transactions_history.brand,
			                 CustomerOfferFeature.__brand__)
			company_id = self.getid(transactions_history.company,
			                 CustomerOfferFeature.__company__)
			category_id = self.getid(transactions_history.category,
			                 CustomerOfferFeature.__category__)
			dept_id = self.getid(transactions_history.dept,
			                 CustomerOfferFeature.__dept__)
			chain_id = self.getid(transactions_history.chain,
			                 CustomerOfferFeature.__chain__)

			dollar = transactions_history.purchase_dollar
			amount = transactions_history.productsize * transactions_history.purchasequantity
			if dollar <= 0 or amount <= 0:
				continue

			date_distance = self.time_weight(transactions_history.date_distance)
			input = (amount, dollar, date_distance)
			self.set_value("brand", brand_id, input)
			self.set_value("company", company_id, input)
			self.set_value("category", category_id, input)
			self.set_value("dept", dept_id, input)

			self.chain_time.setdefault(chain_id, 0)
			self.chain_time[chain_id] += 1

			self.one_year_shopping_dollar += dollar
			self.one_year_shopping_time += 1

	def set_value(self, name, id, input):
		types = ["amount", "dollar", "time"]
		for i, type in enumerate(types):
			d = getattr(self, name + "_" + type)
			d.setdefault(id, 0)
			d[id] += input[i]

	def getid(self, k, _dict_):
		d = _dict_["key_map"]
		if not k in d:
			d[k] = _dict_["cnt"]
			_dict_["cnt"] += 1
		return d[k]

	def time_weight(self, date_distance):
		if date_distance < 30:
			return 0.5
		elif date_distance < 60:
			return 0.3
		elif date_distance < 120:
			return 0.2
		else:
			return 0.1

	def __str__(self):
		out = StringIO.StringIO()
		repeater = self.offer_history.repeattrips
		out.write("%d '%s" % (repeater, self.offer_history.customer_id))
		feature_list = list(self.dict_feature)
		feature_list.sort()
		for fname in feature_list:
			feature = getattr(self, fname)
			# namespace:
			out.write(" |%s" % fname)
			for k, v in feature.items():
				out.write(" %d:%f" % (k, v))
		out.write(" | ")
		for fname in self.float_feature:
			feature = getattr(self, fname)
			out.write(" %s:%f" % (fname, feature))
		# nominal features:
		offer_id = self.getid(self.offer_info.offer_id,
		                      CustomerOfferFeature.__offer__)
		brand_id = self.getid(self.offer_info.brand,
		                 CustomerOfferFeature.__brand__)
		company_id = self.getid(self.offer_info.company,
		                 CustomerOfferFeature.__company__)
		category_id = self.getid(self.offer_info.category,
		                 CustomerOfferFeature.__category__)

		out.write(" offer_%d" % offer_id)
		out.write(" category_%s" % category_id)
		out.write(" brand_%s" % brand_id)
		out.write(" company_%s" % company_id)
		out.seek(0)
		str_self = out.next()
		out.close()
		return str_self