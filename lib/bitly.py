__author__ = 'nibesh'

import bitly_api

from django.conf import settings

b = bitly_api.Connection(access_token=settings.BITLY_ACCESS_TOKEN)


def shorten(url):
    """

    :param url:
    :return:
    """
    try:
        r = b.shorten(url)
        return r['url']
    except bitly_api.BitlyError:
        return url
