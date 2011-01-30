#!/usr/bin/env python
import os, site, sys

# add the virtual environment path
site.addsitedir('/home/robbles/.virtualenvs/uiforms/lib/python2.6/site-packages')

# prevent using stdout
sys.stdout = sys.stderr

# Calculate the path based on the location of the WSGI script.
project = os.path.dirname(__file__)
workspace = os.path.dirname(project)
sys.path.insert(0, workspace)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()

