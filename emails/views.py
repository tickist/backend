from django.template.response import TemplateResponse
from .models import Email

def show_email(request, key):
    email = Email.get_by_key(key)
    return TemplateResponse(request, 'emails/show_email.html', locals())

