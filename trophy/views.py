__author__ = 'nibesh'

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required

from lib.utils import json_response
from lib.tw import search_numbers, twilio_purchase_number, update_sms_callback_url

from route.models import Conversation, Message

from .models import TrophyModel
from .forms import TrophyForm


@csrf_exempt
@login_required
@require_POST
def add_trophy(request):
    form = TrophyForm(request.POST)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        trophy = cleaned_data['trophy'].lower()
        try:
            TrophyModel.objects.get(trophy=trophy, dealer=request.user)
            form.add_error('trophy', 'The trophy "%s" has already been added by the user.' % trophy)
            return json_response(success=False, errors=form.errors)
        except TrophyModel.DoesNotExist:

            o = TrophyModel()
            o.dealer = request.user
            o.trophy = trophy
            o.message = cleaned_data['message']
            o.save()
        return json_response(success=True, message='New Trophy Added !!')
    return json_response(success=False, errors=form.errors)


@csrf_exempt
@login_required
@require_POST
def edit_trophy(request, o_id):
    form = TrophyForm(request.POST)
    if form.is_valid():
        try:
            o = TrophyModel.objects.get(pk=o_id)
        except TrophyModel.DoesNotExist:
            return json_response(success=False, message='Invalid Object.')
        cleaned_data = form.cleaned_data
        o.trophy = cleaned_data['trophy'].lower()
        o.message = cleaned_data['message']
        o.default_order_response = cleaned_data['default_order_response']
        o.enabled = True
        o.save()
        return json_response(success=True, message="Trophy Edited.")
    return json_response(success=False, errors=form.errors)


@login_required
@require_GET
def get_trophy(request, o_id):
    """

    :param request:
    :param o_id:
    :return:
    """
    try:
        o = TrophyModel.objects.get(pk=o_id)
        return json_response(success=True, data={'trophy': o.trophy, 'message': o.message,
                                                 'default_order_response': o.default_order_response})
    except TrophyModel.DoesNotExist:
        return json_response(success=False, message='Invalid Request.')


@require_GET
def get_default_response(request, conversation_id):
    """

    :param request:
    :param o_id:
    :return:
    """
    try:
        o = Conversation.objects.get(pk=conversation_id)
        return json_response(success=True, data={'default_order_response': o.trophy.default_order_response})
    except TrophyModel.DoesNotExist:
        return json_response(success=False, message='Invalid Request.')


@login_required
@require_GET
def delete_trophy(request, o_id):
    try:
        o = TrophyModel.objects.get(pk=o_id)
        o.trophy = ''
        o.message = ''
        o.enabled = False
        o.save()
    except TrophyModel.DoesNotExist:
        pass
    return json_response(success=True, message='Trophy Delete Successful !!')


@csrf_exempt
@login_required
def search(request):
    """

    :param request:
    :return:
    """
    if request.method == 'POST':
        near_number = request.POST.get('near_number', '')
        contains = request.POST.get('contains', '')
        postal_code = request.POST.get('postal_code', '')

        numbers = search_numbers(postal_code, contains, near_number)
        return render(request, 'purchase_number.html', {'numbers': numbers})

    return render(request, 'purchase_number.html')


@login_required
def purchase(request, number):
    """

    :param request:
    :param number:
    :return:
    """
    try:
        phone_number = twilio_purchase_number(number)
        update_sms_callback_url(request, phone_number)
        user = request.user
        t = TrophyModel(dealer=user, twilio_mobile=number, enabled=False)
        t.save()
    except Exception:
        return HttpResponse('Something went wrong. Couldn\'t purchase the number. Please try again')
    return HttpResponse('You have successfully purchased the twilio phone number %s' % number)


@login_required
@require_GET
def get_trophy_conversations(request, trophy_id):
    """

    :param request:
    :param trophy_id:
    :return:
    """
    try:
        t = TrophyModel.objects.get(pk=trophy_id)
        conversations = Conversation.objects.filter(trophy=t, closed=False).order_by('date')
        c_messages = [{'conversation_id': item.id, 'customer_image': item.customer.profile_image,
                       'has_new_message': item.has_new_message, 'customer_username': item.customer.username,
                       'customer_id': item.customer.id,
                       'recent_message': Message.objects.filter(conversation=item).order_by('-id')[0].message} for item
                      in conversations]
        c_n = Conversation.objects.filter(dealer=request.user, has_new_message=True, closed=False).values('trophy_id')
        t_n = list(set([v['trophy_id'] for v in c_n]))
        return json_response(success=True, data=c_messages, new_conv_trop=t_n)

    except TrophyModel.DoesNotExist:
        return json_response(success=False, message='Invalid Request.')
