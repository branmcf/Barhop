
import json

from django.http import HttpResponse

from django.contrib.sites.shortcuts import get_current_site


def json_response(**kwargs):
    """

    :param kwargs:
    :return:
    """
    response = HttpResponse(json.dumps(kwargs), content_type="application/json")
    response["Access-Control-Allow-Origin"] = '*'
    return response


def get_current_url(request):
    """

    :param request:
    :return:
    """
    current_site = get_current_site(request)
    domain = current_site.domain
    protocol = 'https' if request.is_secure() else 'http'
    return '%s://%s' % (protocol, domain)
