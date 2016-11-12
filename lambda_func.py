import urllib2
import json

def get_txns():
	content = urllib2.urlopen("http://intuit-mint.herokuapp.com/api/v1/user/transactions").read()
	return json.loads(content)

def net_income():
	txns = get_txns()
	income = sum([txn['amount'] for txn in txns if txn['amount'] > 0])

	s = "Your net income is {}".format(income)
	return s

def net_expenditure():
	txns = get_txns()
	expenditure = -sum([txn['amount'] for txn in txns if txn['amount'] < 0])

	s = "Your net expenditure is {}".format(expenditure)
	return s


def expense_for(query):
	txns = get_txns()
	expenditure = -sum([txn['amount'] for txn in txns if query.lower() in txn['category'].lower() or query.lower() in txn['name'].lower()])


	s = "Your net expenditure for {} is {}".format(query, expenditure)
	return s
	# print income



#print net_income()
#print net_expenditure()
print expense_for('Fast Food')