__author__ = 'nibesh'

from twilio import twiml

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET

from t_auth.models import RefNewUser, CustomUser

from block.models import BlockModel

from lib.utils import json_response
from lib.tw import send_new_user_message, send_message

from route.forms import OrderReadyForm
from route.models import Conversation, Message
from route.utils import (parse_sms, get_user_by_mobile, get_trophy_by_twilio_mobile, get_ref_user_by_mobile)


from ws4redis.redis_store import RedisMessage
from ws4redis.publisher import RedisPublisher


@require_POST
@csrf_exempt
def handle_sms(request, dealer_id):
    """

    :param request:
    :return:
    """

    from_, body = parse_sms(request.POST)

    r = twiml.Response()
    trophy = get_trophy_by_twilio_mobile(dealer_id)

    if trophy is None:
        return HttpResponse(str(r))

    dealer = trophy.dealer

    customer = get_user_by_mobile(from_)

    if customer is None:
        if body.lower() != trophy.trophy.lower():
            return HttpResponse(str(r))

        ru = get_ref_user_by_mobile(from_)
        if ru:
            send_new_user_message(request, dealer_id, from_, ru.id)
        else:
            a = RefNewUser(dealer=dealer, dealer_mobile=dealer_id, mobile=from_, trophy=body.lower())
            a.save()
            send_new_user_message(request, dealer_id, from_, a.id)
        return HttpResponse(str(r))

    if customer.is_active is False:
        # ru = get_ref_user_by_mobile(from_)
        message = 'Your account is not active yet. Please activate your account by following link your in your email.'
        send_message(dealer_id, from_, message)
        return HttpResponse(str(r))

    try:
        user_blocked = BlockModel.objects.get(blocker=dealer, blocked_user=customer)
        if user_blocked:
            return HttpResponse(str(r))
    except BlockModel.DoesNotExist:
        pass

    try:
        c = Conversation.objects.get(dealer=dealer, customer=customer, closed=False, trophy=trophy)
        c.has_new_message = True
        c.save()
    except Conversation.DoesNotExist:
        c = Conversation(dealer=dealer, customer=customer, trophy=trophy)
        c.save()

    redis_publisher = RedisPublisher(facility='barhop', users=[dealer.username])
    message = RedisMessage("Hello world")
    redis_publisher.publish_message(message)

    m = Message(conversation=c, message=body, direction=True)
    m.save()
    if body.lower() == trophy.trophy.lower():
        reply = trophy.message
        m = Message(conversation=c, message=reply, direction=False)
        m.save()

        send_message(dealer_id, from_, reply)

    return HttpResponse(str(r))


@login_required
@require_GET
def close_conversation(request, conversation_id):
    """

    :param request:
    :param conversation_id:
    :return:
    """
    try:
        c = Conversation.objects.get(pk=conversation_id)
        c.closed = True
        c.save()
    except Conversation.DoesNotExist:
        pass
    return json_response(success=True)


@login_required
@require_GET
def view_conversation(request, conversation_id):
    try:
        c = Conversation.objects.get(pk=conversation_id)
        c.has_new_message = False
        c.save()
    except Conversation.DoesNotExist:
        raise Http404
    ms = Message.objects.filter(conversation=c).order_by('-date')
    messages = [{'message': _.message, 'date': _.date, 'direction': _.direction} for _ in ms]
    customer = c.customer
    return render(request, 'inside_convo.html',
                  {'customer': customer, 'messages': messages, 'conv_id': conversation_id})


@login_required
@require_GET
def ajax_conversation(request, conversation_id):
    try:
        c = Conversation.objects.get(pk=conversation_id)
        c.has_new_message = False
        c.save()
    except Conversation.DoesNotExist:
        raise json_response(sucess=False, data=[])

    ms = Message.objects.filter(conversation=c).order_by('-date')
    messages = [{'message': _.message, 'direction': _.direction} for _ in ms]

    return json_response(success=True, data=messages)


@csrf_exempt
@login_required
@require_POST
def order_ready(request):
    """

    :param request:
    :return:
    """
    form = OrderReadyForm(request.POST)
    if form.is_valid():
        try:
            customer_id = int(request.POST['customer_id'])
            conversation_id = int(request.POST['conversation_id'])
            c = Conversation.objects.get(pk=conversation_id)

        except (ValueError, KeyError, Conversation.DoesNotExist):
            form.add_error('message', 'Invalid Form')
            return json_response(success=False, errors=form.errors)

        message = form.cleaned_data['message']
        customer = CustomUser.objects.get(pk=customer_id)

        m = Message(conversation=c, message=message, direction=False)
        m.save()
        send_message(c.trophy.twilio_mobile, customer.mobile, message)
        return json_response(success=True, message='Order Ready Message Sent.')
    return json_response(success=False, errors=form.errors)


def prettify_number(number):
    """

    :param number:
    :return:
    """
    a = number[-10:]
    return a[0:3] + '-' + a[3:6] + '-' + a[6:10]
