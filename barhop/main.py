__author__ = 'nibesh'

from django.shortcuts import render

from trophy.models import TrophyModel
from route.models import Conversation, Message
from managed_account.models import PurchaseOrder, Trigger
from t_auth.models import CustomUser, DealerEmployeMapping



def how_it_works(request):
    """

    :param request:
    :return:
    """
    return render(request, 'how_it_works.html')


def about_us(request):
    """

    :param request:
    :return:
    """
    return render(request, 'about_us.html')


def contact_us(request):
    """

    :param request:
    :return:
    """
    return render(request, 'contact.html')


def pricing(request):
    """

    :param request:
    :return:
    """
    return render(request, 'pricing.html')