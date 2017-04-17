from django.conf import settings

from django.http.response import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView,CreateView, FormView, DetailView, View, DeleteView

from django.core import serializers
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string

import stripe
import json
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic.edit import UpdateView

from payment.models import PaymentModel,ManagedAccountStripeCredentials, BankAccount
from route.models import Conversation, Message
from trophy.models import TrophyModel

from t_auth.models import CustomUser, DealerEmployeMapping
from .models import  Trigger,Grid,GridDetails, MenuItems, PurchaseOrder, OrderMenuMapping 

from .forms import BankAccountCreationForm, ManagedAccountCreationForm, AddTriggerForm, GridForm,BankAccountEditForm
from t_auth.forms import CustomUserCreationForm

from lib.tw import send_new_user_message, send_message, send_multimedia_message
from t_auth.utils import send_email_auth
from managed_account import utils
from django.db.models import Sum

grid_name_list = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

class HomeView(TemplateView):
    template_name = "dealer/index.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        """

        :param request:
        :return:
        """
        data = {}
        warning_message = ""
        if request.user.is_authenticated():
            
            trophies = TrophyModel.objects.filter(dealer=request.user).order_by('-date')
            c_messages = []
            data = []
            
            try :
                dealer = utils.get_dealer(request.user)
                trigger_id = request.GET.get('trigger')

                dealer_grid = Grid.objects.filter(dealer=dealer)
                warning_message = ''
                if not dealer_grid:
                    warning_message += "Kindly add the Grid details to process your orders.<br>"

                dealer_bankaccount = BankAccount.objects.filter(dealer=dealer)
                if not dealer_bankaccount:
                    warning_message += "Kindly add the bank account details.<br>"

                dealer_triggers = Trigger.objects.filter(dealer=dealer)
                if not dealer_triggers:
                    warning_message += "Kindly add Triggers to get orders.<br>" 
                if trigger_id:
                    current_trigger = Trigger.objects.get(id=int(trigger_id))
                    purchase_paid_orders = PurchaseOrder.objects.filter(dealer=dealer, order_status='PAID', trigger=current_trigger)
                    purchase_ready_orders = PurchaseOrder.objects.filter(dealer=dealer, order_status='READY', trigger=current_trigger)

                    for order in purchase_paid_orders:
                        order_details = {}
                        items = OrderMenuMapping.objects.filter(order=order)
                        order_details['id'] = order.id
                        order_details['items'] = items
                        order_details['order_code'] = order.order_code
                        order_details['total_amount_paid'] = order.total_amount_paid
                        order_details['order_status'] = order.order_status
                        order_details['expires'] = order.expires
                        data.append(order_details)
                else:
                    purchase_paid_orders = PurchaseOrder.objects.filter(dealer=dealer, order_status='PAID')
                    purchase_ready_orders = PurchaseOrder.objects.filter(dealer=dealer, order_status='READY')                    
                    for order in purchase_paid_orders:
                        order_details = {}
                        items = OrderMenuMapping.objects.filter(order=order)
                        order_details['id'] = order.id
                        order_details['items'] = items                        
                        order_details['order_code'] = order.order_code
                        order_details['total_amount_paid'] = order.total_amount_paid
                        order_details['order_status'] = order.order_status
                        order_details['expires'] = order.expires
                        data.append(order_details)
                        

                context['triggers'] = dealer_triggers
                context['trophies'] = trophies
                # context['con_messages'] = c_messages
                context['purchase_paid_orders'] = data
                # context['location'] = order.order_grid_detail.location
                context['purchase_ready_orders'] = purchase_ready_orders

                context['warning_message'] = warning_message
                return render(request, self.template_name, context)
            except:
                pass
            return render(request, self.template_name, context)


        return render(request, 'landing.html')

    # def post(self, request):
    #     order_code = request.POST['order_code']
    #     return None

    def post(self, request):
        data = {}
        django_messages = []
        try:
            order_code = request.POST['order_code']

            dealer = utils.get_dealer(request.user)

            purchase_ready_orders = PurchaseOrder.objects.filter(dealer=dealer, order_status='READY', order_code__icontains=order_code)
            data['purchase_ready_orders'] = purchase_ready_orders
            html = render_to_string('managed_account/orders_to_close.html',data)
            return HttpResponse(html)
        except:
            data['success'] = "False"
            data['error_msg'] = "something went WRONG"
            return HttpResponse(json.dumps(data), content_type='application/json')
        return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
def account_home(request):
    return render(request, 'managed_account/account_main.html')


@login_required
def account_status(request):
    """

    :param request:
    :return:
    """
    user = request.user
    try:
        ma = ManagedAccountStripeCredentials.objects.get(dealer=user)
    except ManagedAccountStripeCredentials.DoesNotExist:
        return redirect(reverse('managed_account:create_account'))
    stripe_secret_key = ma.secret_key
    stripe.api_key = stripe_secret_key

    balance = stripe.Balance.retrieve()
    available_amount = '%.2f' % float(balance['available'][0]['amount'] / 100.0)
    pending_amount = '%.2f' % float(balance['pending'][0]['amount'] / 100.0)
    pa = PaymentModel.objects.filter(dealer=user, processed=True).order_by('-date')
    transactions = [{'date': _.date, 'amount': "%.2f" % float(_.amount / 100.0), 'charge_id': _.charge_id,
                     'description': _.detail, 'tip': "%.2f" % float(_.tip / 100.0),
                     'sales_tax': "%.2f" % float(_.sales_tax / 100.0)} for _ in pa]
    return render(request, 'managed_account/account_status.html',
                  {'available_amount': available_amount, 'pending_amount': pending_amount,
                   'transactions': transactions})


class BankingView(TemplateView):
    template_name = "managed_account/banking.html"

    def get_context_data(self, **kwargs):
        context = super(BankingView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        login_user = request.user
        dealer = utils.get_dealer(login_user)

        pending_amount = 0
        available_amount = 0

        payment_obj = PaymentModel.objects.filter(dealer=dealer)

        if payment_obj:
            pending_obj = payment_obj.filter(order__order_status="PENDING")
            available_obj = payment_obj.filter(Q(order__order_status="PAID") | Q(order__order_status="READY") | Q(order__order_status="CLOSED"))
            if pending_obj:
                pending_amount = pending_obj.aggregate(Sum('total_amount'))
                pending_amount = pending_amount['total_amount__sum']
            if available_obj:
                available_amount = available_obj.aggregate(Sum('total_amount'))
                available_amount = available_amount['total_amount__sum']

        q1 = Q(order__order_status="PAID",processed=True)
        q2 = Q(order__order_status="READY",processed=True)
        q3 = Q(order__order_status="CLOSED",processed=True)

        context['payment_list'] = payment_obj.filter(q1 | q2 | q3)
        context['pending_amount'] = pending_amount
        context['available_amount'] = available_amount

        try:
            context['bankaccount'] = BankAccount.objects.get(dealer=dealer)
        except:
            pass
        return render(request, self.template_name,context)

class GridView(TemplateView):
    template_name = "managed_account/select_trigger.html"

    def get_context_data(self, **kwargs):
        context = super(GridView, self).get_context_data(**kwargs)
        login_user = self.request.user

        if login_user.is_dealer:
            dealer = login_user
        else:
            user_mapping_obj = DealerEmployeMapping.objects.get(employe=login_user)
            dealer = user_mapping_obj.dealer
        try:
            context['trigger'] = Trigger.objects.filter(dealer=dealer)
        except Trigger.DoesNotExist:
            context['trigger'] = None

        return context

class EditGridView(FormView):
    template_name = "managed_account/grid.html"
    form_class = GridForm
    success_url = '/account/grid/'
    model = Grid

    def get_context_data(self, **kwargs):
        context = super(EditGridView, self).get_context_data(**kwargs)
        trigger_id = self.kwargs.get('pk')
        login_user = self.request.user
        context['trigger_id'] = trigger_id

        if login_user.is_dealer:
            dealer = login_user
        else:
            user_mapping_obj = DealerEmployeMapping.objects.get(employe=login_user)
            dealer = user_mapping_obj.dealer
        try:
            context['trigger'] = Trigger.objects.filter(dealer=dealer)
        except Trigger.DoesNotExist:
            context['trigger'] = None

        try:
            trigger = Trigger.objects.get(id=trigger_id)
            context['trigger_name'] = trigger.trigger_name
            grid = Grid.objects.get(trigger=trigger)
            context['grid'] = grid
        except:
            grid = ''

        return context

    def form_valid(self, form):

        trigger_id = self.request.POST.get('trigger_id')
        login_user = self.request.user
        trigger = Trigger.objects.get(id=trigger_id)

        grid, created = Grid.objects.get_or_create(trigger=trigger)
        grid.grid_row = row = form.cleaned_data['grid_row']
        grid.grid_column = col = form.cleaned_data['grid_column']

        if login_user.is_dealer:
            dealer = login_user
        else:
            user_mapping_obj = DealerEmployeMapping.objects.get(employe=login_user)
            dealer = user_mapping_obj.dealer

        grid.dealer = dealer
        grid.created_by = login_user
        

        if not created:
            grid_data = GridDetails.objects.filter(grid=grid)
            active_grid_data = grid_data.filter(is_active=True)
            if active_grid_data:
                message = "You cant update grid now. There is a pending order to be deallocated from the grid"
                messages.success(self.request, message)
                return super(EditGridView, self).form_valid(form)
            else:
                grid.save()
                GridDetails.objects.filter(grid=grid).delete()

        grid_total = row * col

        # =========== Grid Location =============
        
        grid_counter_data = []
        for i in range(row):            
            for k in range(col):
                location = grid_name_list[i]
                location = location + str(k+1)
                grid_counter_data.append(location)

        #======================================

        for gridDetail in range(grid_total):            
            gridDetailobj= GridDetails(grid=grid)
            gridDetailobj.grid_counter = gridDetail
            gridDetailobj.location = grid_counter_data[gridDetail]
            gridDetailobj.save()

        message = "Updated the grid details for the trigger : %s"%(trigger.trigger_name)
        messages.success(self.request, message)

        return super(EditGridView, self).form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class TriggerView(FormView):
    model = Trigger
    form_class = AddTriggerForm
    template_name = 'managed_account/triggers.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super(TriggerView, self).get_context_data(**kwargs)
        user = self.request.user
        try:
            employee_data = DealerEmployeMapping.objects.get(employe=user)
            if employee_data:
                dealer = employee_data.dealer
        except:
            dealer = user
        context['trigger_data'] = Trigger.objects.filter(dealer=dealer)
        return context

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form, **kwargs)
        else:
            return self.form_invalid(form, **kwargs)

    def form_valid(self, form):
        trigger_name = form.cleaned_data['trigger_name']
        login_user = self.request.user

        if login_user.is_dealer:
            dealer = login_user
        else:
            user_mapping_obj = DealerEmployeMapping.objects.get(employe=login_user)
            dealer = user_mapping_obj.dealer

        obj = Trigger(trigger_name=trigger_name, dealer=dealer, created_by=login_user )
        obj.save()
        return super(TriggerView, self).form_valid(form)


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TriggerView, self).dispatch(*args, **kwargs)

class TriggerEditView(View):
    model = Trigger
    success_url = '/accounts/triggers/'

    def get(self,request,*args,**kwargs):
        trigger_name = request.GET.get("trigger_name", "")
        trigger_name = trigger_name.strip()
        data = {}
        if trigger_name:
            try:
                trigger = Trigger.objects.get(id=request.GET.get("trigger_id",""))
                trigger.trigger_name = trigger_name
                trigger.save()

                data['status'] = 'success'
                data['success_message'] = ''

            except:

                data['status'] = 'failed'
                data['success_message'] = 'This name already exists'
        else:
            data['status'] = 'failed'
            data['success_message'] = 'please enter a name'

        return HttpResponse(json.dumps(data), content_type="application/json")


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TriggerEditView, self).dispatch(*args, **kwargs)

class TriggerDeleteView(DeleteView):
    model = Trigger
    template_name = 'managed_account/delete_trigger.html'
    success_url = '/account/triggers/'

    def post(self, *args, **kwargs):
        trigger_id = kwargs['pk']

        '''
        There may not be a grid created
        '''

        try:
            grid = Grid.objects.get(trigger__id=trigger_id)
            griddetails = GridDetails.objects.filter(grid=grid)
            grid.delete()
            griddetails.delete()

        except:
            pass

        return self.delete(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL.
        """

        self.object = trigger = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()

        message = "Deleted the trigger : %s"%(trigger.trigger_name)
        messages.success(self.request, message)

        return HttpResponseRedirect(success_url)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TriggerDeleteView, self).dispatch(*args, **kwargs)

class UsersView(FormView):
    template_name = "managed_account/users.html"
    form_class = CustomUserCreationForm

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        user = self.request.user

        try:
            employee_data = DealerEmployeMapping.objects.get(employe=user)
            if employee_data:
                dealer = employee_data.dealer
        except:
            dealer = user

        context = self.get_context_data(**kwargs)
        context['form'] = form
        context['employe_list'] = DealerEmployeMapping.objects.filter(dealer=dealer, is_active=True).exclude(employe__id=user.id)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form, **kwargs)
        else:
            return self.form_invalid(form, **kwargs)

    def form_invalid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        user = self.request.user
        dealer = utils.get_dealer(self.request.user)
        context['employe_list'] = DealerEmployeMapping.objects.filter(dealer=dealer, is_active=True).exclude(employe__id=user.id)
        context['form'] = form
        return self.render_to_response(context)

    def form_valid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = form
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        login_user = self.request.user


        try :
            user = CustomUser(username=username, email=email, is_active=True, is_staff=False)
            user.set_password(password)
            user.save()

            # checking user type 
            if login_user.is_dealer:
                dealer = login_user
            else:
                user_mapping_obj = DealerEmployeMapping.objects.get(employe=login_user)
                dealer = user_mapping_obj.dealer

            trophy = TrophyModel.objects.get(dealer=dealer)
            DealerEmployeMapping(dealer=dealer, employe=user, trophy_model=trophy,created_by=login_user, is_active=True).save()

            # ------> mail to employe <------
            # ip = self.request.META.get('REMOTE_ADDR')
            # message_body = render_to_string('mail_template/mail_newEmploye.html',
            #     {'dealer_name': dealer.username,
            #     'ip':ip,
            #     'username': username,
            #     'password':password })
            # subject = 'Bar-Hope'
            # to_email = [email]
            # send_email_auth(subject,message_body,to_email)
            #------------------------

        except:
            pass
            
        context['employe_list'] = DealerEmployeMapping.objects.filter(dealer=dealer, is_active=True).exclude(employe=login_user)
        return self.render_to_response(context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UsersView, self).dispatch(*args, **kwargs)

class DeleteEmployeView(View):

    def get_context_data(self, request, *args,**kwargs):
        context = super(DeleteEmployeView, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        django_messages = []
        try:
            user_id = request.POST['data']
            employe = CustomUser.objects.get(id=user_id)
            username = employe.username
            employe.delete()
            data['error_msg'] = ""
            data['success'] = "True"
            messages.success(request, "Successfully deleted the employe "+username)

            for message in messages.get_messages(request):
                django_messages.append({
                    "level": message.level,
                    "message": message.message,
                    "extra_tags": message.tags
                })
            data['messages'] = django_messages
            return HttpResponse(json.dumps(data), content_type='application/json')
        except:
            data['error_msg'] = "something went WRONG"
            return HttpResponse(json.dumps(data), content_type='application/json')

class ChangePasswordView(View):

    def post(self, request):
        data = {}
        django_messages = []

        try:
            user = CustomUser.objects.get(id=request.POST['user_id'])
            password = request.POST['password']
            user.set_password(password)
            user.save()
            data['error_msg'] = ""
            data['success'] = "True"
            messages.success(request, "Password Changed Successfully.")

            # ------> mail new password to employe <------
            # message_body = render_to_string('mail_template/mail_passwordchange.html',
            #     {'username': user.username,
            #     'password':password })
            # subject = 'Password Change'
            # to_email = [ user.email ]
            # send_email_auth(subject,message_body,to_email)
            #------------------------

            for message in messages.get_messages(request):
                django_messages.append({
                    "level": message.level,
                    "message": message.message,
                    "extra_tags": message.tags
                })
            data['messages'] = django_messages
            return HttpResponse(json.dumps(data), content_type='application/json')
        except:
            data['error_msg'] = "something went WRONG"
            return HttpResponse(json.dumps(data), content_type='application/json')

class ChangeAccessLeveView(View):

    def post(self, request):
        data = {}
        django_messages = []
        try:
            user = CustomUser.objects.get(id=request.POST['user_id'])
            if user.is_staff:
                user.is_staff = False
            else:
                user.is_staff = True
            user.save()
            data['error_msg'] = ""
            data['success'] = "True"
            messages.success(request, "Employe : '"+user.username+"' Access Level Changed Successfully.")

            for message in messages.get_messages(request):
                django_messages.append({
                    "level": message.level,
                    "message": message.message,
                    "extra_tags": message.tags
                })
            data['messages'] = django_messages
            return HttpResponse(json.dumps(data), content_type='application/json')
        except:
            data['error_msg'] = "something went WRONG"
            return HttpResponse(json.dumps(data), content_type='application/json')


#=========================== Order Ready & Close ======================================== 

class OrderReadyView(View):

    def post(self, request):
        data = {}
        django_messages = []
        try:
            order_id = request.POST['order_id']
            purchase_order_obj = PurchaseOrder.objects.get(id=order_id)
            purchase_order_obj.order_status = 'READY'

            trigger = Trigger.objects.get(id=purchase_order_obj.trigger.id)            
            grid = trigger.grid_trgger.all()[0]
            
            grid_detail_obj = GridDetails.objects.filter(grid=grid, is_active=False)
            
            # row = grid.grid_row
            # column = grid.grid_column
            # for i in range(row):
            #     for k in range(column):
            #         location = list[i]
            #         location = location + str(k+1)
            #         select_grid = grid_detail_obj.filter(grid_counter=location,is_active=False)

            #         if select_grid.count() > 0:
            #             select_grid = GridDetails.objects.get(grid_counter=counter, grid=grid)
            #             select_grid.order = purchase_order_obj
            #             select_grid.is_active = True
            #             select_grid.save()


            # ================================#
            # Finidng the least counter grid  #
            # ================================#
            counter_list = []
            for grid_detail in grid_detail_obj:
                counter_list.append(grid_detail.grid_counter)
            counter = min(counter_list)
            
            # ==================================== #
            # Updating the grid with purchase order
            # ==================================== #
            grid_detail = GridDetails.objects.get(grid_counter=counter, grid=grid)
            grid_detail.order = purchase_order_obj
            grid_detail.is_active = True
            grid_detail.save()
            
            purchase_order_obj.save()

            data['error_msg'] = ""
            data['success'] = "True"

            order_closed = PurchaseOrder.objects.filter(id=order_id)
            data['purchase_ready_orders'] = order_closed 
            html = render_to_string('dealer/order_ready.html', data)

            #========== Send Message =============
            customer = purchase_order_obj.customer
            customer_mob = customer.mobile
            message = "Your Order is Ready! Your Order Code is '"+ str(purchase_order_obj.order_code) +"'. Come to the bar, Thank you."
            vendor_number = settings.BARHOP_NUMBER
            send_message(vendor_number, customer_mob, message)

            return HttpResponse(html)
            # return HttpResponse(json.dumps(data), content_type='application/json')
        except:
            data['error_msg'] = "something went WRONG"
            return HttpResponse(json.dumps(data), content_type='application/json')
        return HttpResponse(json.dumps(data), content_type='application/json')


class OrderCloseView(View):
    def post(self, request):
        data = {}
        django_messages = []
        try:

            order_id = request.POST['order_id']
            purchase_order_obj = PurchaseOrder.objects.get(id=order_id)
            purchase_order_obj.order_status = 'CLOSED'
            purchase_order_obj.save()

            #====== Close Conversation =====
            customer = purchase_order_obj.customer
            conversation = Conversation.objects.get(customer=customer, closed=False)
            conversation.closed = True
            conversation.save()

            #=========== Grid Updation ============ 
            grid_detail = GridDetails.objects.get(order=purchase_order_obj, is_active=True)
            grid_detail.is_active = False
            grid_detail.order = None
            grid_detail.save()

            data['error_msg'] = ""
            data['success'] = "True"
            return HttpResponse(json.dumps(data), content_type='application/json')
        except:
            data['error_msg'] = "something went WRONG"
            return HttpResponse(json.dumps(data), content_type='application/json')
        return HttpResponse(json.dumps(data), content_type='application/json')


class GetNewOrder(View):
    
    def post(self, request):
        
        data = {}
        django_messages = []
        order_list = []
        try:
            order_id_data = request.POST.get('order_data')
            if order_id_data:
                order_id_data = order_id_data.split(',')
                order_id_data = list(set(order_id_data))
                order_id_data = [ str(i) for i in order_id_data ]
                print (order_id_data)

            data['error_msg'] = ""
            data['success'] = "True"

            dealer = utils.get_dealer(request.user)
            purchase_paid_orders = PurchaseOrder.objects.filter(dealer=dealer, order_status='PAID').exclude(id__in=order_id_data)

            if purchase_paid_orders.count() >= 0:
                for order in purchase_paid_orders:
                    order_details = {}
                    items = OrderMenuMapping.objects.filter(order=order)
                    order_details['id'] = order.id
                    order_details['items'] = items
                    order_details['order_code'] = order.order_code
                    order_details['total_amount_paid'] = order.total_amount_paid
                    order_details['order_status'] = order.order_status
                    order_details['expires'] = order.expires
                    order_list.append(order_details)

                data['purchase_paid_orders'] = order_list
                html = render_to_string('dealer/new_order.html',data)
            else:
                html = ''
            return HttpResponse(html)
            #return HttpResponse(json.dumps(data), content_type='application/json')
        except :
            data['error_msg'] = "something went WRONG"
            return HttpResponse(json.dumps(data), content_type='application/json')
        return HttpResponse(json.dumps(data), content_type='application/json')


# ______________________________________________________________________________________


#=================================== MENU ===============================================#

class MenuListView(FormView):
    template_name = "managed_account/menu.html"

    def get(self, request, *args, **kwargs):
        # form_class = self.get_form_class()
        # form = self.get_form(form_class)
        context = self.get_context_data(**kwargs)
        user = self.request.user
        try:
            employee_data = DealerEmployeMapping.objects.get(employe=user)
            if employee_data:
                dealer = employee_data.dealer
        except:
            dealer = user

        context['menu_data'] = MenuItems.objects.filter(dealer=dealer)

        return self.render_to_response(context)


    def post(self, request, *args, **kwargs):
        data = {}
        django_messages = []
        try:
            table_data = request.POST.getlist("table")

            received_json_data=json.loads(table_data[0])

            for dat in received_json_data:
                try:
                    item_id = int(dat['item_id'])
                    menu_obj = MenuItems.objects.get(id=item_id)
                    
                    if dat['item_name'] == '':
                        data['error_msg'] = "ID : "+ str(item_id) +" , Cannot save this item without name"
                        data['success'] = "False"
                        return HttpResponse(json.dumps(data), content_type='application/json')

                    menu_obj.item_name = dat['item_name']                  
                    menu_obj.item_price = dat['price']
                    menu_obj.quantity_available = dat['quantity']
                    menu_obj.save()
                        
                except:
                    pass
            data['error_msg'] = ""
            data['success'] = "True"
            messages.success(request, "Changes saved successfully.")

            for message in messages.get_messages(request):
                django_messages.append({
                    "level": message.level,
                    "message": message.message,
                    "extra_tags": message.tags
                })
            data['messages'] = django_messages

            return HttpResponse(json.dumps(data), content_type='application/json')
        except:
            data['error_msg'] = "Could not save your changes. Please try again."
            data['success'] = "False"
            return HttpResponse(json.dumps(data), content_type='application/json')


    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MenuListView, self).dispatch(*args, **kwargs)


class AddNewMenuView(View):

    def post(self, request):
        data = {}
        django_messages = []
        try:
            dealer = utils.get_dealer(self.request.user)
            MenuItems.objects.create(dealer=dealer, item_name='')
            data['error_msg'] = ""
            data['success'] = "True"

            return HttpResponse(json.dumps(data), content_type='application/json')
        except:
            data['error_msg'] = "something went WRONG"
            data['success'] = "False"
            return HttpResponse(json.dumps(data), content_type='application/json')
        return HttpResponse(json.dumps(data), content_type='application/json')

#_________________________________________________________________________________#


# ================================== Banking ==================================== #

class AddBankAccountView(FormView):
    template_name = 'managed_account/add_bank_account.html'
    form_class = BankAccountCreationForm
    success_url = '/account/banking/'
    model = BankAccount

    def get_context_data(self, **kwargs):
        context = super(AddBankAccountView, self).get_context_data(**kwargs)
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        return context

    def form_valid(self, form):


        country = form.cleaned_data['country']
        currency = form.cleaned_data['currency']
        routing_number = form.cleaned_data['routing_number']
        account_number = form.cleaned_data['account_number']
        name = form.cleaned_data['name']
        account_holder_type = form.cleaned_data['account_holder_type']
        dealer = utils.get_dealer(self.request.user)

        # ================================================= #
        # Creating managed account for the dealer in barhop
        # stripe platform
        # ================================================= #
        try:
            
            stripe_token = self.request.POST['stripeToken']
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            bankaccount = BankAccount(dealer=dealer,country=country,currency=currency,routing_number=routing_number,
                                      account_number=account_number,name=name,account_holder_type=account_holder_type,stripeToken=stripe_token)
            bankaccount.save()

            stripe_account = stripe.Account.create(country=country, managed=True, external_account=stripe_token)
            stripe_acct = ManagedAccountStripeCredentials(bank_account=bankaccount, dealer=dealer, account_id=stripe_account['id'])
            stripe_acct.save()

        except:
            pass

        message = "Successfully added account details"
        messages.success(self.request, message)
        return super(AddBankAccountView, self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AddBankAccountView, self).dispatch(*args, **kwargs)


class EditBankAccount(UpdateView):
    template_name = 'managed_account/add_bank_account.html'
    form_class = BankAccountEditForm
    model = BankAccount
    success_url = "/account/banking/"

    def get_context_data(self, **kwargs):
        context = super(EditBankAccount, self).get_context_data(**kwargs)
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        return context

    def form_valid(self, form):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        dealer = utils.get_dealer(self.request.user)
        stripe_token = self.request.POST['stripeToken']
        bank_id = self.kwargs['pk']
        managedaccount = ManagedAccountStripeCredentials.objects.get(bank_account__id=int(bank_id))
        account_id = managedaccount.account_id

        account = stripe.Account.retrieve(account_id)
        account.external_account = stripe_token
        account.save()


        message = "Successfully updated account details"
        messages.success(self.request, message)

        return super(EditBankAccount, self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EditBankAccount, self).dispatch(*args, **kwargs)




