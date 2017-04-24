from app import app, mysql

# filters needed for listing events
@app.template_filter('month')
def year_filter(num):
	abbrs = { 1 : "Jan",
			  2 : "Feb",	
			  3 : "Mar",	
			  4 : "Apr",	
			  5 : "May",	
			  6 : "Jun",	
			  7 : "Jul",	
			  8 : "Aug",	
			  9 : "Sep",	
			  10 : "Oct",	
			  11 : "Nov",	
			  12 : "Dec" }
	abbr = abbrs[num] if abbrs.get(num) else ""
	return abbr

@app.template_filter('money')
def money_filter(val):
	return "${:,.2f}".format(val)

@app.template_filter('url_to_cat')
def url_to_cat_filter(val):
	try:
		return " ".join([ (word.capitalize() if word != 'and' else word) for word in val.split('-') ])
	except:
		return ""

@app.template_filter('cat_to_url')
def cat_to_url_filter(val):
	try:
		return val.replace(' ', '-').lower()
	except:
		return ""

@app.template_filter('list_to_str')
def list_to_str_filter(vals):
	return ", ".join(vals)
	
