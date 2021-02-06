import os
import requests


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


def download_url(url, filename, buffer_size=1024 * 1024 * 25, link=None):
	req = requests.get(url, stream=True)
	total = int(req.headers['Content-Length'])
	gen = req.iter_content(buffer_size)
	fp = open(filename, 'wb+')
	downloaded = 0
	for data in gen:
		downloaded += len(data)
		fp.write(data)
		fp.flush()
	link.progress = 100
	link.save()
	fp.close()
