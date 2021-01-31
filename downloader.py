from time import sleep
from server import Link
from shrapnel import merge, download_url, shred


def main():
	while True:
		links = Link.query().filter(progress=100, operator='<').all()
		for link in links:
			download_url(link.url, 'static/downloads/' + link.name, link=link)
		sleep(2)


if __name__ == '__main__':
	main()
