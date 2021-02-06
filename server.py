from flask import Flask, render_template, request, jsonify
from socket import gethostname
from nanorm import *
from shrapnel import shred
import os
import json

set_db_name('markI.db')


class Link(Model):
	url = CharField()
	name = CharField()
	progress = IntegerField()


app = Flask(__name__)


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/download/', methods=['POST'])
def download():
	link = Link()
	link.url = request.form['url']
	link.name = request.form['filename']
	link.save()
	return json.dumps({'status': 'success'})


@app.route('/downloads/')
def downloads():
	links = Link.query().all()
	filtered = []
	for link in links:
		if link.progress == 100:
			filtered.append({
				'url': link.url,
				'href': '/static/downloads/' + link.name,
				'index': link.id
			})
	return json.dumps(filtered)


@app.route('/progress/')
def progress():
	links = Link.query().all()
	filtered = []
	for link in links:
		if link.progress < 100:
			filtered.append({
				'url': link.url,
				'progress': link.progress
			})
	return json.dumps(filtered)


@app.route('/split_download/<_id>/')
def split_download(_id):
	link = Link.get(id=_id)
	folder = 'static/downloads/_' + link.name
	if not os.path.exists(folder):
		os.mkdir(folder)
		shred('static/downloads/'+link.name, filename=link.name, output_folder=folder)
	files = [os.path.join(folder, file.name) for file in os.scandir(folder)]
	return render_template('split_download.html', files=files)


if __name__ == '__main__':
	print(gethostname())
	app.run("0.0.0.0", port=int(os.environ["PORT"]),debug=True)
