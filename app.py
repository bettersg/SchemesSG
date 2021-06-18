from flask import Flask, request, render_template
import sys
import os
import schemes_model as schemes_model
from models import api as models_api
import flask.json as json
from flask_cors import CORS, cross_origin


app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
@cross_origin()

@app.route('/')
def root():
	return render_template('index.html')

@app.route('/index.html')
def index():
	return render_template('index.html')

@app.route('/schemesbank.html')
def schemesbank():
	return render_template('schemesbank.html')

@app.route('/schemespal.html')
def schemespal():
	return render_template('schemespal.html')

@app.route('/schemescase.html')
def schemescase():
	return render_template('schemescase.html')

@app.route('/listing.html')
def listing():
	return render_template('listing.html')

@app.route('/team.html')
def team():
	return render_template('team.html')

@app.route('/update.html')
def update():
	return render_template('update.html')

@app.route('/gotit.html')
def gotit():
	return render_template('gotit.html')

@app.route('/about.html')
def about():
	return render_template('about.html')


@app.route('/schemespredict', methods=['get','post'])
def schemes_predict():
	result = 'nil'
	try:
		input = request.get_json()
		query = input['query']
		result = models_api.search_similar_schemes(query)
	except Exception as e:
		print('Error: ',e)
	return result

if __name__ == '__main__':
	port = int(os.getenv("PORT",9099))
	app.run(host='0.0.0.0',port=port,debug=True)