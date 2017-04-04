
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
from t_auth.models import CustomUser
from django.http import HttpResponseRedirect
import json
from datetime import datetime, timedelta

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


class PasswordAuthentication(View):
    def post(self, request):
        data = {}

        try:
            password = self.request.POST['password']
            user_id = self.request.POST['user_id']

            user = CustomUser.objects.get(id=user_id)
            if user.check_password(password):
                data['error_msg'] = ""
                data['success'] = "True"
                return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                data['error_msg'] = ""
                data['success'] = "False"
                data['error_msg'] = "wrong password!."
                return HttpResponse(json.dumps(data), content_type='application/json')
        except:
            data['error_msg'] = "Something went wrong.."
            return HttpResponse(json.dumps(data), content_type='application/json')


class PaymentInvoiceView(TemplateView):
    template_name = "payment/order_invoice.html"

    def get_context_data(self, **kwargs):
        context = super(PaymentInvoiceView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):

        data = []
        context = self.get_context_data(**kwargs)
        try:            
            purchase_id = self.kwargs.get('pk')
            purchase_order = PurchaseOrder.objects.get(id=purchase_id)
            order_details = OrderMenuMapping.objects.filter(order=purchase_order)

            #=============== Checking already processed or Not =========================
            try:
                payment_obj = PaymentModel.objects.get(order=purchase_order)
                if payment_obj.processed == True:
                    return HttpResponse("This is not a valid link.")
            except:
                pass

            total_amount = 0
            for order in order_details:
                if order.quantity :
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

            #==========Grand Total===========#grand_total
            grand_total = float(total_amount) + float(tax) + float(tip) + float(settings.APPLICATION_FEE)
            grand_total = int(round(grand_total))

            #======== Payment Model ===========#
            uuid_code = uuid.uuid1()
            short_code = shortuuid.encode(uuid_code)
            bill_number = str(short_code)

            payment_obj, created = PaymentModel.objects.get_or_create(order=purchase_order,
                dealer=purchase_order.dealer,
                customer=purchase_order.customer,
                total_amount=grand_total,
                order_amount=total_amount,
                sales_tax=tax,
                tip=tip,
                )
            if created:
                payment_obj.bill_number=bill_number
                payment_obj.save()

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
            context['process_fee'] = settings.APPLICATION_FEE
            context['user_id'] = purchase_order.customer.id
            context['grand_total'] = grand_total
        except:
            pass
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        application_fee = 0
        payment_id = self.request.POST['id']
        stripe_token = self.request.POST['stripeToken']
        token_type = self.request.POST['stripeTokenType']
        email = self.request.POST['stripeEmail']
        
        payment_obj = PaymentModel.objects.get(id=payment_id)

        current_date = datetime.now()
        time_threshold = current_date + timedelta(hours=1)

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

                # ====================================== #
                # This id for stripe charge . 
                # ====================================== #
                stripe_total_amount = total_amount * 100
                application_fee = int(settings.APPLICATION_FEE*100)
                stripe_charge = stripe.Charge.create(amount=stripe_total_amount, currency='usd', source=stripe_token, description="Process Payment",
                                       application_fee=application_fee, stripe_account=account_id,receipt_email=email)

                payment_obj.stripeToken = stripe_token
                payment_obj.stripeTokenType = token_type
                payment_obj.stripeEmail = email
                payment_obj.charge_id = stripe_charge.id
                payment_obj.detail = "Payment Successful"
                payment_obj.processed = True
                payment_obj.save()

                order_obj = PurchaseOrder.objects.get(id=order_id)
                order_obj.order_status = "PAID"
                order_obj.expires = time_threshold
                order_obj.total_amount_paid = total_amount
                order_obj.save()

                return HttpResponseRedirect('/payment/payment_success/'+str(payment_obj.bill_number))

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
