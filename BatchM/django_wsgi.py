import os
import sys
import django.core.handlers.wsgi

sys.path.append('/root/devops/BatchM')
os.environ["DJANGO_SETTINGS_MODULE"] = "BatchM/settings"
application = django.core.handlers.wsgi.WSGIHandler()
