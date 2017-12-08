# Common classes to form (edit and create)

from django import forms
from django.db.models.fields import NOT_PROVIDED
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import ValidationError

class CreateModelForm(forms.ModelForm):

    def __init__(self, data, *args, **kwargs):

        for field in self.Meta.model._meta.fields:
            if (field.default != NOT_PROVIDED) and field.name not in self.Meta.exclude:
                if field.name not in data or not data[field.name]:
                    data.update({field.name: field.default})

        super(CreateModelForm, self).__init__(data, *args, **kwargs)

