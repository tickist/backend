#-*- coding: utf-8 -*-

import sys

DEBUG = True
PRODUCT = False



# to jest potrzebne, aby nie trzeba było cachować templatów za każdym razem
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',

)

DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': True}

ADDRESS = "http://localhost:8888"

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DOMAIN = "http://localhost:8888"

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'LOCATION': 'unique-snowflake'
    },

    # this cache backend will be used by django-debug-panel
    'debug-panel': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/debug-panel-cache',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 200
        }
    }
}

ALLOWED_HOSTS = ['www.tickist.com', 'tickist.com', 'localhost', 'app.tickist.com']
SOCIAL_AUTH_REDIRECT_IS_HTTPS = False


def custom_show_toolbar(request):
     return True  # Always show toolbar, for example purposes only.


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'tickist.settings.custom_show_toolbar',
}

