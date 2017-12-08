#-*- coding: utf-8 -*-
from django.conf.urls import include, url
#from django.conf.urls.i18n import i18n_patterns as patterns
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from users.registration.views import CheckEmailView, ConfirmEmailView, SimpleRegistrationView, \
    SendEmailAfterRegistrationView

urlpatterns = [
                       url(_(r'^check_email/$'), CheckEmailView.as_view(), name='registration-check_email'),
                       url(_(r'^confirm_email/(?P<key>[\D\d]*)/$'), ConfirmEmailView.as_view(),
                           name='registration-confirm_email'),
                       url(_(r'^send_email/$'), SendEmailAfterRegistrationView.as_view(),
                           name='registration-send_email'),
                       url(_(r'^registration/$'), SimpleRegistrationView.as_view(), name='registration-registration'),

]

# Format suffixes
# urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
