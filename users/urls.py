#-*- coding: utf-8 -*-

from django.conf.urls import include, url
#from django.conf.urls.i18n import i18n_patterns as patterns
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url
from users.views import SendMessageToBoard,  ForgotPassword, Complete_login_user_google_plus, SocialLogin

urlpatterns = [
                       # url(_(r'^user/$'), UserDetail.as_view(), name='user-detail'),
                       # url(_(r'^user/change_password'), ChangePassword.as_view(), name='user-change_password'),
                       # url(_(r'^user/change_user_details'), ChangeUserDetails.as_view(), name='user-change_user_details'),
                       url(_(r'^user/send_message_to_board'), SendMessageToBoard.as_view(), name='user-send_message_to_board'),
                       # url(_(r'^user/change_avatar'), ChangeAvatar.as_view(), name='user-change_avatar'),
                       url(_(r'^user/forgot_password/$'), ForgotPassword.as_view(), name='user-forgot_password'),
                       url(_(r'^test/$'), Complete_login_user_google_plus.as_view(), name="dashboard2"),
                       url(_(r'^sociallogin/$'), SocialLogin.as_view(), name="sociallogin"),
]

# Format suffixes
#urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])
