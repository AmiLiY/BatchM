#!/usr/local/py35/bin/python3
import os
import sys
sys.path.append("/var/www/html/BatchM/BatchM/Batch")
sys.path.append("/var/www/html/BatchM/BatchM")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BatchM.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
