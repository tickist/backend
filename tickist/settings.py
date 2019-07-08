#-*- coding: utf-8 -*-
# Django settings for tickist project.
import os
import sys
import ast
import datetime
from os.path import abspath, dirname, join
from session_cleanup.settings import weekly_schedule

# settings/base.py
import os

# Normally you should not import
# ANYTHING from Django directly into
# your settings, but
# ImproperlyConfigured is an
# exception.
from django.core.exceptions import ImproperlyConfigured

msg ="Set the %s environment variable"


def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = msg % var_name
        raise ImproperlyConfigured(error_msg)


def get_current_year():
    return datetime.datetime.now().year


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__)) + "/../"
sys.path.insert(0, join(PROJECT_ROOT, "apps"))
sys.path.insert(0, join(PROJECT_ROOT, "external_apps"))

DEBUG = ast.literal_eval(os.environ.get("DEBUG", "False"))
PRODUCTION = ast.literal_eval(os.environ.get("PRODUCTION", "True"))
CELERY_ALWAYS_EAGER = ast.literal_eval(os.environ.get("CELERY_ALWAYS_EAGER", "True"))

ADMINS = ()

MANAGERS = ADMINS

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
}

if os.environ.get('DATABASE', None) == 'POSTGRESQL':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': get_env_variable('POSTGRES_DB'),
            'USER': get_env_variable('POSTGRES_USER'),
            'PASSWORD': get_env_variable('POSTGRES_PASSWORD'),
            'HOST': 'db',
            'PORT': '',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(PROJECT_ROOT, 'db.sqlite3'),
        }
    }



# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Warsaw'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False
DATE_FORMAT = "d-m-Y"
DATE_INPUT_FORMATS = ('%d-%m-%Y', '%d-%m-%Y', '%Y-%m-%d')

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True


# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"


# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_URL = '/site_media/'

MEDIA_ROOT = os.environ.get("MEDIA_ROOT")
MEDIA_URL = '/media/'

STATIC_ROOT = os.environ.get("STATIC_ROOT")

STATICFILES_DIRS = (
    ('', os.path.join(PROJECT_ROOT, "static/")),

    )


ALLOWED_HOSTS = ['www.tickist.com', 'tickist.com', 'localhost', 'www.app.tickist.com', 'app.tickist.com']


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

#TODO It is ugly
if PRODUCTION:
    MIDDLEWARE = (
        'django.middleware.gzip.GZipMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'social_django.middleware.SocialAuthExceptionMiddleware'
        # Uncomment the next line for simple clickjacking protection:
        # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
        #'debug_panel.middleware.DebugPanelMiddleware',

    )
else:
    MIDDLEWARE = (
        'django.middleware.locale.LocaleMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'social_django.middleware.SocialAuthExceptionMiddleware',
        # Uncomment the next line for simple clickjacking protection:
        # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get("SECRET_KEY", "tickist_secret_key")

LOGIN_URL = "/#login"


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

ROOT_URLCONF = 'tickist.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'tickist.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',

)


MY_APPS = (
    'statistics',
    'commons',
    'dashboard',
    'dashboard.lists',
    'dashboard.tasks',
    'users.login',
    'users.registration',
    'users',
    'notifications',
    'log_errors'
)

EXTERNAL_APPS = (
    'rosetta',
    'robots',
    'django_extensions',
    'rest_framework',
    'factory',
    'emails',
    'mptt',
    'debug_panel',
    'social_django',
    'session_cleanup',
    'corsheaders',
    'django_celery_results',
    'django_celery_beat',
    'dbbackup'
)

INSTALLED_APPS += MY_APPS
INSTALLED_APPS += EXTERNAL_APPS


TIME_TO_CONFIRM_EMAIL = 168 #hours

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


DOMAIN = "https://app.tickist.com"

#South
SOUTH_TESTS_MIGRATE = False  # we shouldn't use SOUTH in tests
SKIP_SOUTH_TESTS = True

LOGIN_REDIRECT_URL = "/"
#LOGIN_URL = reverse_lazy('users:login')

#social registration
AUTHENTICATION_BACKENDS = (
    'social_core.backends.open_id.OpenIdAuth',
    'social_core.backends.google.GoogleOpenId',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.google.GoogleOAuth',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.yahoo.YahooOpenId',
    'social_core.backends.email.EmailAuth',
    'social_core.backends.username.UsernameAuth',
    'django.contrib.auth.backends.ModelBackend',
)

ADDRESS = "https://"

DEFAULT_AVATAR = "site_media/images/default_images/default_avatar_user.png"
# DEFAULT_AVATAR_SIZES = [(250, 250), (250, 200), (200, 200), (190, 150), (150, 150), (90, 90), (80, 80), (60, 60),
#                  (50, 50), (40, 40), (32, 32), (24, 24)]

DEFAULT_AVATAR_SIZES = [(200, 200), (32, 32), (64, 64), (16, 16), (14, 14)]
DEFAULT_LIST_LOGO = "images/default_images/default_list_logo.png"
DEFAULT_COLOR_LIST = "#2c86ff"

COVERAGE_PATH_EXCLUDES =     \
    [r'external_apps', 'rest_framework']


_ = lambda s: s
LANGUAGE_CODE = 'en'
LANGUAGE_ID = 1
LANGUAGES = (
        ('en', _('English')),
        # ('pl', _('Polski')),
    )

#My own user
AUTH_USER_MODEL = 'users.User'


#Rest framework

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}


EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_HOST_USER = 'notification@tickist.com'
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = ast.literal_eval(os.environ.get("EMAIL_USE_TLS", "True"))
SERVER_EMAIL = EMAIL_HOST_USER
MY_MAIL = "Tickist  <notification@tickist.com>"
EMAIL_PORT = os.environ.get("EMAIL_PORT", "")

if PRODUCTION:
    EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


if 'test' in sys.argv:
       DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3'}

#Django robots
ROBOTS_SITEMAP_URLS = [
    '%s/sitemap.xml' % DOMAIN,
]
ROBOTS_CACHE_TIMEOUT = 60*60*24



SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']


# try:
#     import subprocess
#     args = ["git", "--git-dir", _relative(".git"), "describe", "--abbrev=0", "--tags"]
#     if DEBUG:
#         args = ["git", "--git-dir", _relative(".git"), "describe", "--all", "--always"]
#     VERSION_STRING = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
#     del subprocess
#     del args
# except Exception as e:
#     VERSION_STRING = ""

# Python social auth


#
# FACEBOOK_SOCIAL_AUTH_RAISE_EXCEPTIONS = True
# SOCIAL_AUTH_RAISE_EXCEPTIONS = True
# RAISE_EXCEPTIONS = True

SOCIAL_AUTH_EMAIL_FORM_HTML = 'email_signup.html'
SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = 'example.app.mail.send_validation'
SOCIAL_AUTH_EMAIL_VALIDATION_URL = '/email-sent/'
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

URL_PATH = ''

SOCIAL_AUTH_GOOGLE_OAUTH_SCOPE = [
    'https://www.googleapis.com/auth/plus.login',
    'https://www.googleapis.com/auth/userinfo.email'
]

SOCIAL_AUTH_PIPELINE = (

    'social.pipeline.social_auth.social_details',

    'social.pipeline.social_auth.social_uid',

    'social.pipeline.social_auth.auth_allowed',

    'social.pipeline.social_auth.social_user',

    'users.pipeline.get_username',
    'social.pipeline.mail.mail_validation',
    'users.pipeline.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'users.pipeline.get_avatar',
    'users.pipeline.send_email_to_login_user'
)

GOOGLE_OAUTH2_CLIENT_ID = os.environ.get("GOOGLE_OAUTH2_CLIENT_ID", "")
GOOGLE_OAUTH2_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH2_CLIENT_SECRET", "")
SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get("SOCIAL_AUTH_FACEBOOK_KEY", "")
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get("SOCIAL_AUTH_FACEBOOK_SECRET", "")

SOCIAL_AUTH_GOOGLE_PLUS_KEY = os.environ.get("GOOGLE_OAUTH2_CLIENT_ID", "")
SOCIAL_AUTH_GOOGLE_PLUS_SECRET = os.environ.get("GOOGLE_OAUTH2_CLIENT_SECRET", "")

#email
SETTINGS_VARIABLES_IN_EMAIL = ['FACEBOOK_FANPAGE', 'GOOGLE_PLUS', 'TWITTER', 'DOMAIN', 'CURRENT_YEAR']


#django celery
from datetime import timedelta
CELERY_IMPORTS = ("dashboard.tasks.utils", )
CELERYBEAT_SCHEDULE = {
    'unsuspend_tasks': {
        'task': 'dashboard.tasks.tasks.unsuspend_tasks',
        'schedule': timedelta(hours=1),
    },
    'db_backup': {
        'task': 'commons.tasks.db_backup',
        'schedule': timedelta(days=1),
    },
    'daily_summary': {
        'task': 'notifications.tasks.daily_summary',
        'schedule': timedelta(minutes=5),
    },
    'notifications_send': {
        'task': 'notifications.tasks.send_notifications',
        'schedule': timedelta(minutes=5),
    },
    'session_cleanup': weekly_schedule
}

CELERY_RESULT_BACKEND = 'django-db'

CELERY_TIMEZONE = 'UTC'

CORS_ORIGIN_ALLOW_ALL = True

JWT_AUTH = {
    'JWT_ENCODE_HANDLER':
    'rest_framework_jwt.utils.jwt_encode_handler',

    'JWT_DECODE_HANDLER':
    'rest_framework_jwt.utils.jwt_decode_handler',

    'JWT_PAYLOAD_HANDLER':
    'rest_framework_jwt.utils.jwt_payload_handler',

    'JWT_PAYLOAD_GET_USER_ID_HANDLER':
    'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',

    'JWT_RESPONSE_PAYLOAD_HANDLER':
    'users.utils.jwt_response_payload_handler',

    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 0,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=60*60*24*14), #14 days

    'JWT_ALLOW_REFRESH': False,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),

    'JWT_AUTH_HEADER_PREFIX': 'JWT',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(seconds=60*60*24*14),  #14 days
    'REFRESH_TOKEN_LIFETIME': timedelta(seconds=60*60*24*14),  #14 days
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,

    'AUTH_HEADER_TYPES': ('Authorization', 'JWT'),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    #'TOKEN_TYPE_CLAIM': 'token_type',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}


DBBACKUP_FILENAME_TEMPLATE = 'ticksist-dump-database-{datetime}.{extension}'

CURRENT_YEAR = get_current_year()
FACEBOOK_FAN_PAGE = 'https://www.facebook.com/Tickist/'
TWITTER = 'https://twitter.com/Tickist/'

if PRODUCTION:
    DBBACKUP_STORAGE = 'storages.backends.dropbox.DropBoxStorage'
    DBBACKUP_STORAGE_OPTIONS = {
        'oauth2_access_token': get_env_variable('DROPBOX_OAUTH2_ACCESS_TOKEN'),
    }
else:
    DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
    DBBACKUP_STORAGE_OPTIONS = {'location': '/var/backups/'}

try:
    from settings_local import *
except ImportError:
    pass

