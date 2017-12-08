#-*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
#from Crypto.Cipher import AES
import base64
from django.http import Http404




class Email(models.Model):
    """ Tabela przechowywująca maile """
    topic = models.CharField(max_length=100)
    body = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="email_from_user", null=True, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False, db_column='this_creation_date')
    send_at = models.DateTimeField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    is_send_by_S3 = models.BooleanField(default=False)
    is_send = models.BooleanField(default=True)
    #when it is null, we will send by default email

    key = models.CharField(db_index=True, max_length=60, default="0000000000000000000000000000000000000000")
    original_key = models.CharField(db_index=True, max_length=60, default="0000000000000000000000000000000000000000")

    class Meta:
        ordering = ['id']

    def __init__(self, *args, **kwargs):
        super(Email, self).__init__(*args, **kwargs)
        if not self.key or self.key == '0000000000000000000000000000000000000000':
            self.generate_key()

    def __str__(self):
        return 'Title: ' + str(self.topic) + str(' to: ') + str(self.user)

    def get_absolute_url(self):
        return reverse('emails:show', args=[self.key])

    def generate_key(self):
        import hashlib
        key = "ADFGUEDSE12345#$!#%^@^#&BFmifdsjfiskdoakdposkanfsruehunvushfu,./;[]"

        if self.user:
            email = self.user.username.encode("utf8")
        else:
            email = self.email.encode("utf8")

        new_key = hashlib.sha224(key.encode("utf8") + self.topic.encode("utf8") + email).hexdigest()
        collision = Email.objects.filter(original_key=new_key).count()
        self.original_key = new_key
        if collision:
            new_key += str(collision)

        self.key = new_key


    @staticmethod
    def get_by_key(key):
        try:
            return Email.objects.get(key=key)
        except ObjectDoesNotExist:
            raise Http404
