from app import app, mysql
import numpy as np
import scipy.optimize as opt

def cost_function(params, Y, R, num_events, num_users, num_features, lam):
	X = np.reshape(params[0:num_events*num_features], (num_events, num_features))
	Theta = np.reshape(params[num_events*num_features:], (num_users, num_features))

	"""
	Y_adj = R .* Y;
	diff = (X * Theta' .* R) - Y_adj;
	diff_squared = diff .^ 2;
	J = sum(sum(diff_squared)) / 2;

	X_grad = diff * Theta;
	Theta_grad = diff' * X;

	J += (lambda / 2 * sum(sum(Theta .^ 2))) + (lambda / 2 * sum(sum(X.^ 2)));
	X_grad += (lambda * X);
	Theta_grad += (lambda * Theta);
	"""
	Y_adj = np.multiply(Y, R)
	diff = np.multiply(X.dot(Theta.T), R) - Y_adj
	diff_squared = diff**2
	J = np.sum(diff_squared) / 2
	J += (lam/2*np.sum(Theta**2)) + (lam/2*np.sum(X**2)) # regularization

	return J
	
def get_recommendations():
	# connect to database
	connection = mysql.get_db()
	cursor = connection.cursor()

	cursor.execute("SELECT COUNT(*) FROM Event")
	m_e = cursor.fetchall()[0][0] # number of events
	cursor.execute("SELECT COUNT(*) FROM User")
	m_u = cursor.fetchall()[0][0] # number of users
	n = 10 # number of features

	query = "SELECT e.eid, u.uid, CASE WHEN (e.eid, u.uid) IN (SELECT eid, uid FROM IsInterestedIn) THEN 1 WHEN (e.eid, u.uid) IN (SELECT eid, uid FROM HasRegisteredViews) THEN 0 ELSE NULL END AS rating FROM Event e, User u"
	total = cursor.execute(query)
	result = cursor.fetchall()

	events_dict = np.array([ result[i][0] for i in range(0, total, m_u) ])
	users_dict = np.array([ result[i][1] for i in range(0, m_u) ])

	orig_Y = np.array([ row[2] for row in result ]).reshape((m_e, m_u))
	Y = np.array([ row[2] if row[2] != None else 0 for row in result ]).reshape((m_e, m_u))
	R = np.array([ 1 if row[2] != None else 0 for row in result ]).reshape((m_e, m_u))

	lam = 0
	init_X = np.random.rand(m_e, n)
	init_Theta = np.random.rand(m_u, n)
	params = np.append(np.reshape(init_X, m_e*n), np.reshape(init_Theta, m_u*n))

	print("num_events: {}\tnum_users: {}\tnum_features: {}".format(m_e, m_u, n))
	result = opt.minimize(cost_function, params, args=(Y, R, m_e, m_u, n, lam))
	final_params = result.x
	X = np.reshape(final_params[0:m_e*n], (m_e, n))
	Theta = np.reshape(final_params[m_e*n:], (m_u, n))

	ratings = X.dot(Theta.T)
	ratings = np.multiply(ratings, 1-R) # set the ratings of already interested in events to 0
	limit = 10
	top_rated_events = np.empty((m_u, limit)).astype(int)
	for i in range(m_u):
		top_rated_events[i, :] = ratings[:, i].argsort()[-limit:][::-1]
	for i in range(m_u):
		vals = np.array([ events_dict[j] for j in top_rated_events[i, :] ]).astype(int)
		print("user {} : {}".format(users_dict[i], vals))
