from flask import render_template
from app import app
from app.crawlers.eventful import crawl as eventful_crawl

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/crawl')
def crawl():
	return eventful_crawl()
