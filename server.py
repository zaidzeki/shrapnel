from time import sleep
from flask import Flask, render_template, request, session, redirect
from nanorm import *
from shrapnel import shred, download_url
import os
import json
import _thread
import random

set_db_name('markI.db')
tokens = [
	'SADO_NIHILIST',
	'ACTA,NON VERBA',
	'BEYOND THE SHADOWS'
]
sessions = []


class Link(Model):
	url = CharField()
	name = CharField()
	progress = IntegerField()
	owner = CharField()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'BGKJSDHGDFKJKSGHDSKJFHGKDJF'


@app.route('/', methods=['GET', 'POST'])
def index():
	global sessions
	if request.method == 'POST':
		token = request.form['token']
		if token in tokens:
			session['owner'] = token
		else:
			return redirect('/login')
	elif session.get('owner') is None:
		return redirect('/login')
	return render_template('index.html')


@app.route('/login')
def login():
	return render_template('login.html')


@app.route('/download/', methods=['POST'])
def download():
	link = Link()
	link.url = request.form['url']
	link.name = request.form['filename']
	if not session.get('owner'):
		session['owner'] = get_session()
	link.owner = session.get('owner')
	link.save()
	return json.dumps({'status': 'success'})


@app.route('/downloads/')
def downloads():
	links = Link.query().all()
	filtered = []
	for link in links:
		if link.progress == 100 and link.owner == session.get('owner'):
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
		if link.progress < 100 and link.owner == session.get('owner'):
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
		shred('static/downloads/' + link.name, filename=link.name, output_folder=folder)
	files = [os.path.join(folder, file.name) for file in os.scandir(folder)]
	return render_template('split_download.html', files=files)


@app.route('/settings')
def settings():
	return render_template('settings.html')


def downloader():
	while True:
		links = Link.query().filter(progress=0).all()
		for link in links:
			_thread.start_new_thread(download_url, (link.url, 'static/downloads/' + link.name, 25*1024*1024, link))
		sleep(20)


if __name__ == '__main__':
	_thread.start_new_thread(downloader, ())
	app.run("0.0.0.0", port=int(os.environ.get('PORT', 5885)), debug=True)
