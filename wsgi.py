import os, sys
sys.path.append('/home/django')
sys.path.append('/home/django/Morlunk')
sys.path.append('/usr/lib/python2.6/site-packages/')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Morlunk.settings")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
