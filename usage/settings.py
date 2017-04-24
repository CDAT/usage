################################################################################
#
#                DEFAULT SETTINGS, DO NOT MAKE YOUR CHANGES HERE!
#         YOU MUST HAVE A `local_settings.py` IN ORDER FOR THIS TO RUN
# If you do not have a `local_settings.py, run the following command:
#     cp local_settings.py.template local_settings.py
#
# Then,open local_settings.py in your favorite editor and follow the
# instructions.
# 
# These settings are over-ridden by local_settings.py
# That is where you should make all your changes.
#
# If you would like to change a setting that is not in local_settings.py, copy
# it from this file and make ALL changes in local_settings.py
#
################################################################################
# Documentation that helped in configuration:
# https://code.djangoproject.com/ticket/20400
# for getting around HTTPS: http://stackoverflow.com/questions/35536491/error-youre-accessing-the-development-server-over-https-but-it-only-supports
# in regards to static files: http://stackoverflow.com/questions/30263701/django-1-8-and-the-ever-confusing-static-files
import socket
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if socket.gethostname() == "pcmdi6.llnl.gov":
    from local_settings import *


# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True


SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

import chartkick
# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
  os.path.join(BASE_DIR, 'static/'),                                                
  chartkick.js(),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'OPTIONS': {
#             'read_default_file': '~/export/kuivenhoven1/usage/uvcdat_usage.sql',
#         },
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',# Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'uvcdat_usage',  # Or path to database file if using sqlite3.
        'USER': 'uvcdat_usage',                            # Not used with sqlite3.
        'PASSWORD': '1b29e7fe6839569bd408d29642e40f39e5f75c8f112b53a8414d7a2c9f569972',
        'HOST': 'localhost',                            # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                            # Set to empty string for default. Not used with sqlite3.
        'OPTIONS': {
                    'init_command': 'SET innodb_strict_mode=1',
                            },
    }
}




MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'usage.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'usage.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # '/example/uvcdat/usage/templates'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'stats',
    'statsPage',
    'login',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'twitter_bootstrap',
    'django_extensions',
    # http://django-mysql.readthedocs.io/en/latest/installation.html
    # 'django_mysql'
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'chartkick',
    'world_regions',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console':{
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose'
        },
        'file':{
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# if it exists, override these settings with the ones in local_settings.py
try:
    from local_settings import *
except ImportError:
    pass
