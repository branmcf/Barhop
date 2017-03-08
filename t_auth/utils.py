__author__ = 'nibesh'

import json
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator as token_generator

from django.core.validators import RegexValidator

phone_regex = RegexValidator(regex=r'^\+[1-9][0-9]{10,15}$',
                             message="The required format is +XXXXXXXXXXX with Country code eg +13362688901. The number is 11 to 15 characters long.")


def send_email_verification(request, user):
    subject = '[Barhop] Account Activation'
    current_site = get_current_site(request)
    domain = current_site.domain
    c = {
        'protocol': 'https' if request.is_secure() else 'http',
        'domain': domain,
        'user': user,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token_generator.make_token(user),
    }

    message = render_to_string('authentication/email_verification_email.txt', c)
    user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)


def json_response(status_code=None, **kwargs):
    response = HttpResponse(json.dumps(kwargs), content_type="application/json")
    if status_code:
        response.status_code = status_code
    response["Access-Control-Allow-Origin"] = '*'
    return response

def send_email_auth(subject,message_body,to_email):
    print("Sending mail...")
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(subject,message_body,from_email,to_email,fail_silently=False)