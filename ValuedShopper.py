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
	"""docstring for Features"""

	def __init__(self, customer_file, offer_history, offer_info):
		super(CustomerOfferFeature, self).__init__()
		# history of bought the same brand, no matter what category:
		self.bought_same_brand = [0 for i in range(4)]
		self.bought_diff_brand = self.bought_same_brand
		self.bought_same_company = [0 for i in range(4)]
		self.bought_diff_company = self.bought_same_company
		self.bought_same_exactly = [0 for i in range(4)]
		self.same_exactly_amount_ratio = 0  # 购买了同brand，同company的产品总量和同category产品的比例
		self.same_exactly_dollar_ratio = 0
		self.brand_amount_ratio = 0  # 购买该品牌的总量，占同category产品的比例
		self.brand_dollar_ratio = 0  # 购买该品牌的总价格，占同category产品的比例
		self.company_amount_ratio = 0
		self.company_dollar_ratio = 0
		self.category_dollar_ratio = 0  # 全年购买商品中，该category的总花销比例
		self.category_freq_ratio = 0  # 全年购买商品中，该category的购买次数比例
		# 该offer的quantity和用户平时购买同brand的商品时的quantity是否match
		self.offer_quantity_match = 0
		self.offer_discount = 0  # 同units商品单价的比值，表示打折力度
		self.the_company_dollar_ratio = 0
		self.the_company_freq_ratio = 0
		self.the_brand_dollar_ratio = 0
		self.the_brand_freq_ratio = 0
		# given the same brand as offered, is the company always preffered ?
		self.brand_on_company_loyalty = 0
		# given the same company as offered, is the brand always preffered ?
		self.company_on_brand_loyalty = 0
		self.company_cnt = 0
		self.brand_cnt = 0
		self.category_cnt = 0
		self.dept_cnt = 0
		self.one_year_shopping_cost = 0
		self.everytime_shopping_cost = 0
		# all above are numerate features:
		self.feature_list = self.__dict__.keys()

		self.most_category = ""
		self.most_chain = ""
		self.most_company = ""
		self.most_brand = ""
		self.most_dept = ""
		self.customer_info = CSV(customer_file)
		self.offer_history = offer_history
		self.offer_info = offer_info

	def get(self):
		# 中间变量
		category_dollar_sum = 0
		category_amount_sum = 0
		same_exactly_amount_sum = 0
		same_exactly_dollar_sum = 0
		# 同category、同brand amount之和
		same_brand_amount_sum = 0
		same_brand_dollar_sum = 0
		same_company_amount_sum = 0
		same_company_dollar_sum = 0
		total_shopping_dollar = 0
		category_shopping_time = 0
		total_shopping_time = 0
		same_exactly_shopping_time = 0
		same_exactly_quantity_sum = 0
		# 所有category时，购买该brand的次数和花销
		just_samebrand_shopping_time = 0
		just_samebrand_dollar_sum = 0
		just_samecompany_shopping_time = 0
		just_samecompany_dollar_sum = 0
		same_brand_company_shopping_time = 0
		company_dict = {}
		brand_dict = {}
		dept_dict = {}
		chain_dict = {}
		category_dict = {}

		offer_brand = self.offer_info.brand
		offer_category = self.offer_info.category
		offer_company = self.offer_info.company

		for line in self.customer_info:
			transactions_history = Transactions(line, self.offer_history.offerdate)
			this_dept = transactions_history.dept
			this_brand = transactions_history.brand
			date_distance = transactions_history.date_distance
			this_company = transactions_history.company
			this_category = transactions_history.category
			dollar = transactions_history.purchase_dollar
			amount = transactions_history.productsize * transactions_history.purchasequantity
			total_shopping_time += 1
			total_shopping_dollar += dollar
			time_line = self.get_timeline(date_distance)
			if this_brand == offer_brand:
				just_samebrand_shopping_time += 1
				just_samebrand_dollar_sum += transactions_history.purchase_dollar
				self.bought_same_brand = \
					self.merge_timeline(self.bought_same_brand, time_line)
			else:
				self.bought_diff_brand = \
					self.merge_timeline(self.bought_diff_brand, time_line)

			if this_company == offer_company:
				just_samecompany_shopping_time += 1
				just_samecompany_dollar_sum += transactions_history.purchase_dollar
				self.bought_same_company = \
						self.merge_timeline(self.bought_same_company, time_line)
			else:
				self.bought_diff_company = \
					self.merge_timeline(self.bought_diff_company, time_line)

			if this_company == offer_company and this_brand == offer_brand:
				same_brand_company_shopping_time += 1

			if not this_brand in brand_dict:
				self.brand_cnt += 1
				brand_dict[this_brand] = 0
			if not this_company in company_dict:
				self.company_cnt += 1
				company_dict[this_company] = 0
			if not this_category in category_dict:
				self.category_cnt += 1
				category_dict[this_category] = 0
			if not this_dept in dept_dict:
				self.dept_cnt += 1
				dept_dict[this_dept] = 0

			brand_dict[this_brand] += 1
			company_dict[this_company] += 1
			category_dict[this_category] += 1
			dept_dict[this_dept] += 1
			chain_dict.setdefault(transactions_history.chain, 0)
			chain_dict[transactions_history.chain] += 1

			if this_category == offer_category:
				if this_brand == offer_brand and this_company == offer_company:
					if transactions_history.purchasequantity > 0:
						same_exactly_shopping_time += 1
						same_exactly_amount_sum += amount
						same_exactly_dollar_sum += dollar
						same_exactly_quantity_sum += transactions_history.purchasequantity
						self.bought_same_exactly = self.merge_timeline(\
							self.bought_same_exactly, \
					        time_line)
				if this_brand == offer_brand:
					same_brand_amount_sum += amount
					same_brand_dollar_sum += dollar

				if this_company == offer_company:
					same_company_amount_sum += amount
					same_company_dollar_sum += dollar

				category_dollar_sum += dollar
				category_amount_sum += amount
				category_shopping_time += 1

		self.one_year_shopping_cost = total_shopping_dollar
		self.everytime_shopping_cost = total_shopping_dollar / total_shopping_time
		# 购买了同brand，同company的产品总量和同category产品的比例
		self.same_exactly_amount_ratio = self.limit_ratio(same_exactly_amount_sum, category_amount_sum)
		self.same_exactly_dollar_ratio = self.limit_ratio(same_exactly_dollar_sum, category_dollar_sum)
		# 购买该品牌的总量，占同category产品的比例
		self.brand_amount_ratio = self.limit_ratio(same_brand_amount_sum, category_amount_sum)
		# 购买该品牌的总价格，占同category产品的比例
		self.brand_dollar_ratio = self.limit_ratio(same_brand_dollar_sum, category_dollar_sum)
		self.company_amount_ratio = self.limit_ratio(same_company_amount_sum, category_amount_sum)
		self.company_dollar_ratio = self.limit_ratio(same_company_dollar_sum, category_dollar_sum)
		# 全年购买商品中，该category的总花销比例		
		self.category_dollar_ratio = self.limit_ratio(category_dollar_sum, total_shopping_dollar)
		# 全年购买商品中，该category的购买次数比例
		self.category_freq_ratio = self.limit_ratio(category_shopping_time, total_shopping_time)
		self.the_company_dollar_ratio = self.limit_ratio(just_samecompany_dollar_sum, \
                                                 total_shopping_dollar)
		self.the_company_freq_ratio = self.limit_ratio(just_samecompany_shopping_time, \
		                                               total_shopping_time)
		self.the_brand_dollar_ratio = self.limit_ratio(just_samebrand_dollar_sum, \
		                                               total_shopping_dollar)
		self.the_brand_freq_ratio = self.limit_ratio(just_samebrand_shopping_time, \
		                                             total_shopping_time)
		self.brand_on_company_loyalty = self.limit_ratio(same_brand_company_shopping_time, \
		                                                 just_samebrand_shopping_time)
		self.company_on_brand_loyalty = self.limit_ratio(same_brand_company_shopping_time, \
		                                                 just_samecompany_shopping_time)

		self.most_category = self.most_in_dict(category_dict)
		self.most_chain = self.most_in_dict(chain_dict)
		self.most_company = self.most_in_dict(company_dict)
		self.most_brand = self.most_in_dict(brand_dict)
		self.most_dept = self.most_in_dict(dept_dict)

		# 该offer的quantity和用户平时购买同brand的商品时的quantity是否match
		if same_exactly_shopping_time == 0:
			self.offer_quantity_match = 0
			self.offer_discount = 1
		else:
			if same_exactly_shopping_time == 0 or self.offer_info.quantity == 0:
				self.offer_quantity_match = 0
			else:
				self.offer_quantity_match = float(same_exactly_quantity_sum) / \
				                            same_exactly_shopping_time / \
			                                self.offer_info.quantity
			if same_exactly_quantity_sum == 0 or self.offer_info.quantity == 0:
				self.offer_discount = 1
			else:
				unit_price_before = float(same_exactly_dollar_sum) / same_exactly_quantity_sum
				offer_price = float(self.offer_info.offervalue) / self.offer_info.quantity
				# 同units商品单价的比值，表示打折力度
				self.offer_discount = self.limit_ratio(offer_price, unit_price_before)
	def merge_timeline(self, a, b):
		# todo: 为什么不直接相加呢？
		# or 把amount和purchasevalue都按时间段累加？这样感觉更有区分度
		return [int(i+j > 0) for i,j in zip(a,b)]

	def limit_ratio(self, a, b):
		if a == 0:
			return 0
		elif b == 0:
			return 1
		else:
			return float(a) / b

	def get_timeline(self, date_distance):
		ret = [0, 0, 0, 0]
		if date_distance < 30:
			ret[0] = 1
		elif date_distance < 60:
			ret[1] = 1
		elif date_distance < 120:
			ret[2] = 1
		else:
			ret[3] = 1
		return ret
	def most_in_dict(self, one_dict):
		maxv = 0
		ret = None
		for k, v in one_dict.items():
			if maxv < v:
				maxv = v
				ret = k
		return ret

	def __str__(self):
		out = StringIO.StringIO()
		repeater = self.offer_history.repeater
		out.write("%d '%s" % (repeater, self.offer_history.customer_id))
		time_line_feature = filter(lambda f: f.startswith("bought_"), dir(self))
		other_feature = set(self.feature_list) - set(time_line_feature)
		for f in time_line_feature:
			time_line_list = getattr(self, f)
			for i, x in enumerate(time_line_list):
				out.write(" %s%d:%f" % (f, i, x))
		for f in other_feature:
			out.write(" %s:%f" % (f, getattr(self, f)))
		# nominal features:
		out.write(" offer_%s" % self.offer_info.offer_id)
		out.write(" category_%s" % self.offer_info.category)
		out.write(" brand_%s" % self.offer_info.brand)
		out.write(" company_%s" % self.offer_info.company)
		out.write(" most_brand_%s" % self.most_brand)
		out.write(" most_category_%s" % self.most_category)
		out.write(" most_chain_%s" % self.most_chain)
		out.write(" most_company_%s" % self.most_company)
		out.write(" most_dept_%s" % self.most_dept)
		out.seek(0)
		str_self = out.next()
		out.close()
		return str_self