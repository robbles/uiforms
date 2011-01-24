# Local settings specific to this server

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Captain Nemo', 'nemo@nautilus.io'),
)
MANAGERS = ADMINS

SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'sqlite3',   # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'dev.db',     # Or path to database file if using sqlite3.
        'USER': '',     # Not used with sqlite3.
        'PASSWORD': '', # Not used with sqlite3.
        'HOST': '',     # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',     # Set to empty string for default. Not used with sqlite3.
    }
}

INTERNAL_IPS = ('127.0.0.1')

import logging
logging.basicConfig(
    level = logging.DEBUG if DEBUG else logging.INFO,
    format = '[ %(levelname)s ] %(message)s',
)

# Note: make a new one of these - this is only a sample
SECRET_KEY = '4n9wAdcYyf7`LuWyO`zqOP^PLQfa8jijqc2bTb7S<=r0[_fQ'


