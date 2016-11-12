import urllib2
import json

def get_txns():
	content = urllib2.urlopen("http://intuit-mint.herokuapp.com/api/v1/user/transactions").read()
	return json.loads(content)

def get_net_income():
	txns = get_txns()
	income = sum([txn['amount'] for txn in txns if txn['amount'] > 0])

	s = "Your net income is {}".format(income)
	return s

def get_net_expenditure():
	txns = get_txns()
	expenditure = -sum([txn['amount'] for txn in txns if txn['amount'] < 0])

	s = "Your net expenditure is {}".format(expenditure)
	return s


def expense_for(query):
	txns = get_txns()
	expenditure = -sum([txn['amount'] for txn in txns if query.lower() in txn['category'].lower() or query.lower() in txn['name'].lower()])


	s = "Your net expenditure for {} is {}".format(query.lower(), expenditure)
	return s
	# print income

def get_type(flag):
	if flag == 1:
		return "You top sources of incomes are..."
	else:
		return "You spent the most on..."

# flag = 1 for incomes, flag = -1 for expenses have different intent methods
# and invoke the same method

def stat(flag):
	txns = get_txns()
	cat = {}
	for txn in txns:
		if flag * txn['amount'] > 0:
			txn_cat = txn['category']
			cat[txn_cat] = cat.get(txn_cat, 0) + txn['amount']
	
	stat = sorted(cat.items(), key=lambda x:x[1], reverse=(flag==1))[:3]
	stat = [(s[0],int(flag*s[1])) for s in stat]
	items = ''
	for s in stat:
		items += s[0]+' $'+str(s[1])+","

	resp = '{} {}.'.format(get_type(flag), items[:len(items)-1])
	return resp

	




a = {}
a['a'] = net_income

#print net_income()
#print net_expenditure()
print stat(-1)