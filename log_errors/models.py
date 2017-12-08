import hashlib
from django.db import models
from users.models import User


class LogError(models.Model):

    hash = models.CharField(max_length=255, db_index=True)
    user = models.ForeignKey(User,  on_delete=models.DO_NOTHING)
    creation_date = models.DateTimeField(auto_now_add=True, editable=False, db_column='this_creation_date')
    message = models.CharField(max_length=1000)
    stack = models.TextField()
    location = models.CharField(max_length=255)

    def __unicode__(self):
        return self.message

    def __str__(self):
        return self.message

    def _create_hash(self):
        hash_string = '{},{},{},{}'.format(self.user.id, self.message, self.stack, self.location).encode('utf-8')
        return hashlib.sha1(hash_string).hexdigest()

    def save(self, *args, **kwargs):
        hash = self._create_hash()
        if not LogError.objects.filter(hash=hash).exists():
            self.hash = hash
            super(LogError, self).save(*args, **kwargs)



