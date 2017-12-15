#-*- coding: utf-8 -*-
from uuid import uuid4
from random import randrange
from urllib2 import urlopen, HTTPError
from django.template.defaultfilters import slugify
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from social.pipeline.user import get_username as social_get_username
from emails.utils import async_send_email
from commons.utils import gen_passwd
from django.db.models.loading import get_model
from social_django.models import UserSocialAuth


def get_username(strategy, details, user=None, *args, **kwargs):
    details.update({"username": details['first_name']})
    result = social_get_username(strategy, details, user=user, *args, **kwargs)
    # result['username'] = '-'.join([
    #     result['username'], strategy.backend.name, str(randrange(0, 1000))
    # ])
    return result


def get_avatar(strategy, user=None, *args, **kwargs):
    """
        Get avatar from social media services
    """
    url = None
    _response = kwargs['response']
    if kwargs['backend'].__class__.__name__ == 'FacebookOAuth2':
        url = "http://graph.facebook.com/%s/picture?type=large" % _response.get('id')

        if url:
            try:
                avatar = urlopen(url)
                rstring = uuid4().get_hex()
                photo = avatar.read()
                user.avatar_save(ContentFile(photo, name=slugify(rstring + '_p') + '.jpg'))

            except HTTPError:
                pass
    if kwargs['backend'].__class__.__name__  in user.GOOGLE_CLASS_NAMES:
        image = _response['image'] if 'image' in _response else ""
        url = image['url'] if 'url' in image else ""
        if url:
             try:
                avatar = urlopen(url)
                rstring = uuid4().get_hex()
                photo = avatar.read()
                user.avatar_save(ContentFile(photo, name=slugify(rstring + '_p') + '.jpg'))
             except HTTPError:
                pass

def send_email_to_login_user(strategy, user=None, *args, **kwargs):
    """
        The function sends email to user and change email verification field
    """
    if user and 'is_new' in kwargs and kwargs['is_new']:
        if kwargs['backend'].__class__.__name__ in user.GOOGLE_CLASS_NAMES:
            social_name = "Google"
        elif kwargs['backend'].__class__.__name__ in user.FACEBOOK_CLASS_NAMES:
            social_name = "Facebook"
        else:
            social_name = ""
        user_password = gen_passwd(length=15)
        user.is_confirm_email = True
        user.set_password(user_password)
        user.save()
        async_send_email.apply_async(kwargs={"topic":_("Thank you for registering with Tickist!"),
                                             "template":"registration/email/social_registration.html",
                                            "email":user.email, "data_email": {"password": user_password, "user": user,
                                                     "social_name": social_name}})


def create_user(*args, **kwargs):
    """
        Create user when you register using social media
    """
    user = get_model(settings.AUTH_USER_MODEL).objects.create_user(kwargs['username'], email=kwargs['details']['email']) if not kwargs['user'] else kwargs['user']
    #I don't know if it is necessary
    usersocialauth, created = UserSocialAuth.objects.get_or_create(user=user, uid= kwargs['uid'], provider=kwargs['backend'].name)
    return user