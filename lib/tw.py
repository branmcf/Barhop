__author__ = 'nibesh'

from twilio import exceptions
from twilio.rest import TwilioRestClient

from lib.bitly import shorten
from lib.utils import get_current_url

from django.conf import settings
from django.core.urlresolvers import reverse

client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def send_message(from_, to, message):
    """

    :param from_:
    :param to:
    :param message:
    :return:
    """
    client.messages.create(from_=from_, to=to, body=message)

def send_multimedia_message(from_, to, message, media_url):
    """

    :param from_:
    :param to:
    :param message:
    :return:
    """
    client.messages.create(from_=from_, to=to, body=message, media_url=media_url)


def send_new_user_message(request, from_, to, ref_id):
    """

    :param ref_id:
    :return:
    """
    message = 'Welcome to Barhop, We see you are new ! Please Signup here. '
    url = get_current_url(request) + reverse('new_register')
    url += '?id=' + str(ref_id)
    #url = shorten(url)
    message += ' ' + url
    send_message(from_, to, message)


def send_price_message(request, from_, to_, message, p_id):
    """

    :param request:
    :param from_:
    :param to_:
    :param message:
    :param p_id:
    :return:
    """
    url = get_current_url(request) + reverse('payment:process')
    url += '?id=' + str(p_id)
    message = message + ' Please Process your payment at ' + url
    send_message(from_, to_, message)
    return message


def search_numbers(postal_code=None, contains=None, near_number=None):
    """

    :param postal_code:
    :param contains:
    :param near_number:
    :return:
    """
    return client.phone_numbers.search(country='US', postal_code=postal_code, contains=contains,
                                       near_number=near_number)


def twilio_purchase_number(phone_number):
    """

    :param phone_number:
    :return:
    """
    return client.phone_numbers.purchase(phone_number=phone_number)


def update_sms_callback_url(request, phone_number):
    """

    :param phone_number:
    :param url:
    :return:
    """
    url = get_current_url(request) + reverse('route:sms_forward', kwargs={'dealer_id': phone_number.phone_number})
    return phone_number.update(sms_url=url)
