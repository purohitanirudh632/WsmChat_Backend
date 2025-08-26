import os
from django.core.wsgi import get_wsgi_application

# Set the default Django settings module for the 'wsmChat' project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wsmChat.settings')

# Get WSGI application
application = get_wsgi_application()