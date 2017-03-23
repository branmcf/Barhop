__author__ = 'nibesh'
from django.views.generic import TemplateView,CreateView, FormView, DetailView, View, DeleteView
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

import stripe

from lib.utils import json_response
from lib.tw import send_price_message, send_message

from t_auth.models import CustomUser

from .models import ManagedAccountStripeCredentials

from .models import PaymentModel, RevenueModel
from .forms import PriceSubmissionForm
from lib.tw import send_message
from route.models import Conversation, Message
from managed_account.models import PurchaseOrder, OrderMenuMapping
stripe.api_key = settings.STRIPE_SECRET_KEY

CHARGE_AMOUNT = 50
CHARGE_PERCENT = 0.18
STRIPE_CHARGE_PERCENT = 0.029
STRIPE_CHARGE_AMOUNT = 30
SALES_TAX_PERCENT = 0.0825


@login_required
@csrf_exempt
@require_POST
def send_price(request):
    """

    :param request:
    :return:
    """
    user = request.user

    form = PriceSubmissionForm(request.POST)
    try:
        ManagedAccountStripeCredentials.objects.get(dealer=user)
    except ManagedAccountStripeCredentials.DoesNotExist:
        form.add_error('detail', 'Please add Bank Account first in your profile.')
        return json_response(success=False, errors=form.errors)

    if form.is_valid():
        try:
            customer_id = int(request.POST['customer_id'])
            conversation_id = int(request.POST['conversation_id'])
            c = Conversation.objects.get(pk=conversation_id)
        except (KeyError, Conversation.DoesNotExist, ValueError):
            form.add_error('detail', 'Invalid Form')
            return json_response(success=False, errors=form.errors)

        cleaned_data = form.cleaned_data
        try:
            customer = CustomUser.objects.get(pk=customer_id)
        except CustomUser.DoesNotExist:
            raise Http404

        r_amount = cleaned_data['amount']

        p = PaymentModel(dealer=request.user, customer=customer,
                         amount=r_amount,
                         detail=cleaned_data['detail'], trophy=c.trophy)
        p.save()

        sent_message = send_price_message(request, c.trophy.twilio_mobile, customer.mobile, cleaned_data['detail'],
                                          p.id)
        m = Message(conversation=c, message=sent_message, direction=False)
        m.save()
        return json_response(success=True, message='Price Info has been sent to the client.')
    return json_response(success=False, errors=form.errors)


@login_required
@csrf_exempt
def process_payment(request):
    """
    :param request:
    :return:
    """
    if request.POST:
        try:
            _id = int(request.POST['id'])
            o = PaymentModel.objects.get(pk=_id, processed=False)
        except (ValueError, PaymentModel.DoesNotExist):
            raise Http404

        stripe_token = request.POST['stripeToken']
        stripe_token_type = request.POST['stripeTokenType']
        stripe_email = request.POST['stripeEmail']

        r_amount = o.amount
        d_amount = r_amount + int(r_amount * CHARGE_PERCENT) + CHARGE_AMOUNT + int(r_amount * SALES_TAX_PERCENT)
        application_fee = CHARGE_AMOUNT

        try:
            dealer = o.dealer
            customer = o.customer
            ma = ManagedAccountStripeCredentials.objects.get(dealer=dealer)
            stripe_account = ma.account_id
            res = stripe.Charge.create(amount=d_amount, currency='usd', source=stripe_token, description=o.detail,
                                       application_fee=application_fee, stripe_account=stripe_account,
                                       receipt_email=customer.email)

            r = RevenueModel(dealer=dealer, transaction_amount=o.amount, charge_amount=application_fee)
            r.save()

        except stripe.error.CardError:
            return render(request, 'payment/payment_failed.html', {'_id': _id})

        o.stripeToken = stripe_token
        o.stripeTokenType = stripe_token_type
        o.stripeEmail = stripe_email
        o.charge_id = res.id
        o.processed = True
        o.amount = int(r_amount - STRIPE_CHARGE_AMOUNT - STRIPE_CHARGE_PERCENT * d_amount)
        o.tip = int(d_amount - r_amount - CHARGE_AMOUNT - r_amount * SALES_TAX_PERCENT)
        o.sales_tax = int(r_amount * SALES_TAX_PERCENT)
        o.save()

        try:
            c = Conversation.objects.get(dealer=o.dealer, customer=o.customer, closed=False, trophy=o.trophy)
        except Conversation.DoesNotExist:
            c = Conversation(dealer=o.dealer, customer=o.customer, trophy=o.trophy)
            c.save()

        message = 'We have received your payment of $%.2f. We will let you know when the order is ready' % (
            (d_amount / 100.0))
        m = Message(conversation=c, message=message, direction=False)
        m.save()

        send_message(o.trophy.twilio_mobile, o.customer.mobile, message)
        return HttpResponse('Payment Successful.')

    _id = int(request.GET.get('id'))
    try:
        o = PaymentModel.objects.get(pk=_id, processed=False)
    except PaymentModel.DoesNotExist:
        raise Http404

    r_amount = o.amount
    d_amount = r_amount + int(r_amount * CHARGE_PERCENT) + CHARGE_AMOUNT + int(r_amount * SALES_TAX_PERCENT)
    # d_amount = int(d_amount * (100 / 97.1))

    data = {
        'id': _id,
        'data_key': settings.STRIPE_PUBLIC_KEY,
        'data_amount': d_amount,
        'data_name': 'Barhop',
        'data_description': o.detail,
    }

    return render(request, 'payment/payment.html', {'data': data})

class PaymentInvoiceView(TemplateView):
    template_name = "payment/order_invoice.html"

    def get_context_data(self, **kwargs):
        context = super(PaymentInvoiceView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        data = []
        context = self.get_context_data(**kwargs)
        purchase_id = self.kwargs.get('pk')
        purchase_order = PurchaseOrder.objects.get(id=purchase_id)
        order_details = OrderMenuMapping.objects.filter(order=purchase_order)

        grand_total = 0
        for order in order_details:
            item = {}
            item['item_name'] = order.menu_item.item_name
            item['quantity'] = order.quantity
            item['price'] = order.menu_item.item_price
            item['total'] = order.total_item_amount
            grand_total += order.total_item_amount
            data.append(item)
        context['order_details'] = data
        context['grand_total'] = grand_total

        return render(request, self.template_name, context)


class PaymentSuccessView(TemplateView):
    template_name = "payment/payment_success.html"

    def get_context_data(self, **kwargs):
        context = super(PaymentSuccessView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        from_ = '+12145714438'
        message = "Your payment of '100$' has recieved.Your order number is [ORDER NUMBER]. We'll text you when your drink is ready! "
        vendor_number = settings.BARHOP_NUMBER
        send_message(vendor_number, from_, message)

        return render(request, self.template_name, context)