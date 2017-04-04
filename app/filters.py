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
