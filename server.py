from time import sleep
from flask import Flask, render_template, request, jsonify
from socket import gethostname
from nanorm import *
from shrapnel import shred, download_url
import os
import json
import _thread

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


def downloader():
	while True:
		links = Link.query().filter(progress=100, operator='<').all()
		for link in links:
			download_url(link.url, 'static/downloads/' + link.name, link=link)
		sleep(2)


if __name__ == '__main__':
	_thread.start_new_thread(downloader, ())
	os.environ['PORT'] = '5885'
	app.run("0.0.0.0", port=int(os.environ['PORT']), debug=True)
