from time import sleep
from flask import Flask, render_template, request, session, redirect
from nanorm import *
import os
import json
import _thread
import requests
import sys

set_db_name('markI.db')
resources = json.load(open('resources.json'))
config = json.load(open('config.json'))


class Link(Model):
	url = CharField()
	name = CharField()
	progress = IntegerField()
	owner = CharField()


class Token(Model):
	token = CharField()
	admin = BooleanField()


class Shrapnel:
	@staticmethod
	def shred(filepath, filename=None, output_folder='', buffer_size=1024 * 1024 * 5):
		if filename is None:
			abs_path = os.path.abspath(filepath)
			split = abs_path.rfind(os.sep)
			filename = abs_path[split + 1:]
		fp = open(filepath, 'rb+')
		data = fp.read(buffer_size)
		i = 0
		while len(data):
			fpo = open(os.path.join(output_folder, '{}_{}'.format(i, filename)), 'wb+')
			fpo.write(data)
			fpo.flush()
			fpo.close()
			i += 1
			data = fp.read(buffer_size)
		fp.close()

	@staticmethod
	def merge(filename, output_folder):
		fpo = open(os.path.join(output_folder, filename), 'wb+')
		i = 0
		while True:
			fname = '{}_{}'.format(i, filename)
			if not os.path.exists(fname):
				break
			fp = open(fname, 'rb')
			fpo.write(fp.read())
			fpo.flush()
			fp.close()
			i += 1
		fpo.close()

	@staticmethod
	def download_url(url, filename, buffer_size=1024 * 1024 * 25, link=None):
		s = requests.session()
		req = s.get(url, stream=True, allow_redirects=True)
		total = int(req.headers.get('Content-Length', -1))
		gen = req.iter_content(buffer_size)
		fp = open(filename, 'wb+')
		downloaded = 0
		for data in gen:
			downloaded += len(data)
			if link is not None and total != -1:
				link.progress = (downloaded * 100) // total
				link.save()
			fp.write(data)
			fp.flush()
		link.progress = 100
		link.save()
		fp.close()


if len(Token.query().all()) == 0:
	token = Token()
	token.token = 'ZEKI_ZED'
	token.admin = True
	token.save()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'JNHSKLBbvlsjebiuadkajfnLKFNAKJFNKSjnfkajnfkj'


@app.route('/')
def index():
	if not check_session(session):
		return redirect('/login')
	return render_template('index.html', is_admin=check_session(session, is_admin=True), **resources)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		token = request.form['token']
		tokens = Token.query().filter(token=token).all()
		if len(tokens) > 0:
			session['owner'] = token
			return redirect('/')
		else:
			return render_template('login.html', error=True, **resources)
	return render_template('login.html', **resources)


@app.route('/download', methods=['POST'])
def download():
	link = Link()
	link.url = request.form['url']
	link.name = request.form['filename']
	if not check_session(session):
		return json.dumps({'status': 'Unauthorized'})
	link.owner = session.get('owner')
	link.save()
	return json.dumps({'status': 'success'})


@app.route('/status')
def status():
	if not check_session(session):
		return json.dumps({'status': "Unauthorized"})
	links = Link.query().all()
	progress = []
	downloads = []
	for link in links:
		if link.progress == 100 and link.owner == session.get('owner'):
			entry = {
				'name': link.name,
				'href': '/static/downloads/' + link.name,
				'index': link.id
			}
			try:
				size = os.stat('static/downloads/' + link.name).st_size
				entry['size'] = human_readable(size)
			except Exception as e:
				print(e)
			downloads.append(entry)
		if link.progress < 100 and link.owner == session.get('owner'):
			progress.append({
				'name': link.name,
				'progress': link.progress
			})
	return json.dumps({
		"status": "success",
		"progress": progress,
		"downloads": downloads
	})


@app.route('/split_download/<_id>/')
def split_download(_id):
	if not check_session(session):
		return redirect('/login')
	link = Link.get(id=_id)
	folder = 'static/downloads/_' + link.name
	if not os.path.exists(folder):
		os.mkdir(folder)
		Shrapnel.shred(
			'static/downloads/' + link.name,
			filename=link.name,
			output_folder=folder,
			buffer_size=config['buffer_size']
		)
	files = [os.path.join(folder, file.name) for file in os.scandir(folder)]
	return render_template('split_download.html', files=files, **resources)


@app.route('/settings')
def settings():
	if not check_session(session, is_admin=True):
		return redirect('/')
	return render_template('settings.html', **resources)


@app.route('/settings_api', methods=['GET', 'POST'])
def settings_api():
	if not check_session(session, is_admin=True):
		return json.dumps({"status": "Unauthorized"})
	config['tokens'] = [{"token": token.token, "is_admin": token.admin} for token in Token.query().all()]
	if request.method == 'GET':
		return json.dumps(config)
	else:
		keys = request.form.keys()
		for key in keys:
			value = request.form.get(key)
			if value.isnumeric():
				config[key] = int(value)
			elif value == 'true':
				config[key] = True
			elif value == 'false':
				config[key] = False
			else:
				config[key] = value
		tokens = json.loads(config['tokens'])
		token_tokens = [token['token'] for token in tokens]
		for token in tokens:
			the_tokens = Token.query().filter(token=token['token']).all()
			if len(the_tokens) == 0:
				new_token = Token()
				new_token.token = token['token']
				new_token.admin = token['is_admin']
				new_token.save()
			if len(the_tokens) == 1 and the_tokens[0].admin != token['is_admin']:
				the_tokens[0].admin = token['is_admin']
				the_tokens[0].save()
		for token in Token.query().all():
			if token.token not in token_tokens:
				links = Link.query().filter(owner=token.token).all()
				for link in links:
					file = 'static/downloads/' + link.name
					folder = 'static/downloads/_' + link.name
					print(folder)
					if os.path.exists(file):
						print('A')
						os.remove(file)
					if os.path.exists(folder):
						print('B')
						[os.remove(file.path) for file in os.scandir(folder)]
						os.removedirs(folder)
					link.delete()
				token.delete()
		del config['tokens']
		fp = open('config.json', 'w+')
		json.dump(config, fp)
		fp.flush()
		fp.close()
		return json.dumps({'status': 'success'})


@app.route('/logout')
def logout():
	if check_session(session):
		del session['owner']
	return redirect('/login')


def downloader():
	downloading = []
	while True:
		links = Link.query().filter(progress=100, operator='<').all()
		for link in links:
			if link.id not in downloading:
				_thread.start_new_thread(
					Shrapnel.download_url,
					(link.url, 'static/downloads/' + link.name, 25 * 1024 * 1024, link)
				)
				downloading.append(link.id)
		sleep(2)


def human_readable(size):
	if size < 1024:
		return str(size)[:6] + " b"
	if size < 1024 * 1024:
		return str(size / 1024)[:6] + " kb"
	if size < 1024 * 1024 * 1024:
		return str(size / (1024 * 1024))[:6] + " Mb"
	return str(size / (1024 * 1024 * 1024))[:6] + " Gb"


def check_session(session, is_admin=False):
	owner = session.get('owner')
	if owner is None:
		return False
	tokens = Token.query().filter(token=owner).all()
	if len(tokens) == 1:
		if is_admin:
			token = tokens[0]
			if not token.admin:
				return False
		return True
	return False


if __name__ == '__main__':
	args = sys.argv[1:]
	if len(args) >= 2:
		if args[0] == 'merge':
			Shrapnel.merge(args[1], '')
			exit()
		elif args[0] == 'shred':
			Shrapnel.shred(args[1])
			exit()
	_thread.start_new_thread(downloader, ())
	app.run("0.0.0.0", port=int(os.environ.get('PORT', 5885)), debug=True)
