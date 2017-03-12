from flask import render_template
from app import app
from app.crawlers.eventful import crawl as eventful_crawl

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/eventcreate')
def event_create():
	return render_template('eventcreate.html')

@app.route('/signUp')
def sign_up():
    return render_template('signUp.html')

@app.route('/crawl')
def crawl():
	return eventful_crawl()
