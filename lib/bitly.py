__author__ = 'nibesh'

import bitly_api

from django.conf import settings

# b = bitly_api.Connection(access_token=settings.BITLY_ACCESS_TOKEN)

bitly = bitly_api.Connection(settings.BITLY_USER_LOGIN, settings.BITLY_API_KEY)

def shorten(url):
    """

    :param url:
    :return:
    """
    try:
        r = bitly.shorten(url)
        return r['url']
    except bitly_api.BitlyError:
        return url
