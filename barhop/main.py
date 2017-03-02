__author__ = 'nibesh'

from django.shortcuts import render

from trophy.models import TrophyModel
from route.models import Conversation, Message


def index(request):
    """

    :param request:
    :return:
    """
    if request.user.is_authenticated():
        trophies = TrophyModel.objects.filter(dealer=request.user).order_by('-date')
        c_messages = []
        if trophies:
            conversations = Conversation.objects.filter(dealer=request.user, closed=False, trophy=trophies[0]).order_by(
                'date')
            c_messages = [(item, Message.objects.filter(conversation=item).order_by('-id')[0]) for item in
                          conversations]
        return render(request, 'dealer/index.html', {'trophies': trophies, 'con_messages': c_messages})
    return render(request, 'landing.html')


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
    return render(request, 'contact_us.html')
