import os
from tarfile import TarFile

if not os.path.exists('run.py'):
	fp = TarFile('package.tar')
	fp.extractall()

import run
