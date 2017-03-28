__author__ = 'nibesh'
from django.views.generic import TemplateView,CreateView, FormView, DetailView, View, DeleteView
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import uuid
import stripe
import shortuuid

from lib.utils import json_response
from lib.tw import send_price_message, send_message

from t_auth.models import CustomUser

from .models import ManagedAccountStripeCredentials

from .models import PaymentModel, RevenueModel
from .forms import PriceSubmissionForm
from lib.tw import send_message
from route.models import Conversation, Message
from managed_account.models import PurchaseOrder, OrderMenuMapping
from django.http import HttpResponseRedirect

stripe.api_key = settings.STRIPE_SECRET_KEY

CHARGE_PERCENT = 0.18
STRIPE_CHARGE_PERCENT = 0.029
STRIPE_CHARGE_AMOUNT = 30
SALES_TAX_PERCENT = 0.0825


def get_tax(amount):
    tax_percent = settings.SALES_TAX_PERCENT
    tax = (amount*tax_percent)/100
    return tax

def get_tip(amount):
    tip_percent = settings.BARHOP_TIP
    tip = (amount*tip_percent)/100
    return tip

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

        total_amount = 0
        for order in order_details:
            item = {}
            item['item_name'] = order.menu_item.item_name
            item['quantity'] = order.quantity
            item['price'] = order.menu_item.item_price
            item['total'] = order.total_item_amount
            total_amount += order.total_item_amount
            data.append(item)

        #========== Tax and Tip ===========#
        tax = get_tax(total_amount)
        tip = get_tip(total_amount)

        #==========Grand Total===========#
        grand_total = float(total_amount) + float(tax) + float(tip) + float(settings.APPLICATION_FEE)
        grand_total = int(round(grand_total))

        #======== Payment Model ===========#
        uuid_code = uuid.uuid1()
        short_code = shortuuid.encode(uuid_code)
        bill_number = str(short_code)

        payment_obj = PaymentModel.objects.create(order=purchase_order,
            dealer=purchase_order.dealer,
            customer=purchase_order.customer,
            total_amount=grand_total,
            order_amount=total_amount,
            sales_tax=tax,
            tip=tip,
            bill_number=bill_number,
            )

        # ====================================================== #
        # This is to get the whole value in stripe. For example 
        # if we do not add *100 , stripe will convert $126 into
        # 1.26 dollors.
        # ====================================================== #
        stripe_checkout_data = {
            'id': payment_obj.id,
            'data_key': settings.STRIPE_PUBLIC_KEY,
            'data_amount': grand_total*100,
            'data_name': 'Barhop',
            'data_description': "test",
        }

        context['order_details'] = data
        context['data'] = stripe_checkout_data
        context['tax'] = tax
        context['tip'] = tip
        context['grand_total'] = grand_total 

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        payment_id = self.request.POST['id']
        stripe_token = self.request.POST['stripeToken']
        token_type = self.request.POST['stripeTokenType']
        email = self.request.POST['stripeEmail']
        
        payment_obj = PaymentModel.objects.get(id=payment_id)

        try:
            if payment_obj:
                
                total_amount = int(payment_obj.total_amount)
                dealer = payment_obj.dealer
                customer = payment_obj.customer
                order_id = payment_obj.order.id
                
                try:
                    dealer_stripe_account = ManagedAccountStripeCredentials.objects.get(dealer=dealer)
                    account_id = dealer_stripe_account.account_id
                except:
                    account_id = None
                
                stripe_charge = stripe.Charge.create(amount=total_amount, currency='usd', source=stripe_token, description="payment",
                                       application_fee=settings.APPLICATION_FEE, stripe_account=account_id,receipt_email=email)

                payment_obj.stripeToken = stripe_token
                payment_obj.stripeTokenType = token_type
                payment_obj.stripeEmail = email
                payment_obj.charge_id = stripe_charge.id
                payment_obj.detail = "Payment Successful"
                payment_obj.processed = True
                payment_obj.save()

                order_obj = PurchaseOrder.objects.get(id=order_id)
                order_obj.order_status = "PAID"
                order_obj.total_amount_paid = total_amount
                order_obj.save()

                return HttpResponseRedirect('/payment_success/'+str(payment_obj.bill_number))

        except stripe.error.CardError:
            return render(request, 'payment/payment_failed.html', {'_id': _id})

class PaymentSuccessView(TemplateView):
    template_name = "payment/payment_success.html"

    def get_context_data(self, **kwargs):
        context = super(PaymentSuccessView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        bill_number = self.kwargs.get('bill_num')
        try:
            payment_obj = PaymentModel.objects.get(bill_number=bill_number)
            customer_mob = payment_obj.customer.mobile
            context['payment_data'] = payment_obj

            conversation = Conversation.objects.get(customer=payment_obj.customer, dealer=payment_obj.dealer, closed=False)
            conversation.process_stage = 7
            conversation.save()
        except:
            context['payment_data'] = ''
            pass

        message = "Your payment of '$"+str(payment_obj.total_amount)+"' has recieved.Your order number is '"+str(payment_obj.order.order_code)+"' . We'll text you when your drink is ready! "
        vendor_number = settings.BARHOP_NUMBER
        send_message(vendor_number, customer_mob, message)

        return render(request, self.template_name, context)
