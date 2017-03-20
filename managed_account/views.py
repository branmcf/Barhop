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

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from payment.models import PaymentModel,ManagedAccountStripeCredentials
from route.models import Conversation, Message
from trophy.models import TrophyModel

from t_auth.models import CustomUser, DealerEmployeMapping
from .models import  Trigger,Grid,GridDetails, MenuItems, PurchaseOrder

from .forms import BankAccountCreationForm, ManagedAccountCreationForm, AddTriggerForm, GridForm
from t_auth.forms import CustomUserCreationForm

from t_auth.utils import send_email_auth
from managed_account import utils


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
        if request.user.is_authenticated():
            trophies = TrophyModel.objects.filter(dealer=request.user).order_by('-date')
            c_messages = []
            if trophies:
                conversations = Conversation.objects.filter(dealer=request.user, closed=False, trophy=trophies[0]).order_by(
                    'date')
                c_messages = [(item, Message.objects.filter(conversation=item).order_by('-id')[0]) for item in
                              conversations]
            try :
                dealer = utils.get_dealer(request.user)
                trigger_id = request.GET.get('trigger')
                
                if trigger_id:
                    trigger = Trigger.objects.get(id=trigger_id)
                    purchase_paid_orders = PurchaseOrder.objects.filter(dealer=dealer, order_status='PAID', trigger=trigger)
                    purchase_ready_orders = PurchaseOrder.objects.filter(dealer=dealer, order_status='READY', trigger=trigger)
                else:
                    purchase_paid_orders = PurchaseOrder.objects.filter(dealer=dealer, order_status='PAID')
                    purchase_ready_orders = PurchaseOrder.objects.filter(dealer=dealer, order_status='READY')
                
                triggers = Trigger.objects.filter(dealer=dealer)
                context['triggers'] = triggers
                context['trophies'] = trophies
                context['con_messages'] = c_messages
                context['purchase_paid_orders'] = purchase_paid_orders
                context['purchase_ready_orders'] = purchase_ready_orders
                return render(request,self.template_name ,context)
            except:
                pass
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

        payment_list = PaymentModel.objects.filter(dealer=dealer)
        context['payment_list'] = payment_list
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
        grid.save()

        if not created:
            GridDetails.objects.filter(grid=grid).delete()

        m = row * col

        for gridDetail in range(m):            
            gridDetailobj= GridDetails(grid=grid)
            gridDetailobj.grid_counter = gridDetail
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

            counter_list = []
            for grid_detail in grid_detail_obj:
                counter_list.append(grid_detail.grid_counter)
            counter = min(counter_list)
            
            grid_detail = GridDetails.objects.get(grid_counter=counter)
            grid_detail.grid = grid
            grid_detail.order = purchase_order_obj
            grid_detail.grid_counter = counter
            grid_detail.is_active = True
            grid_detail.save()

            purchase_order_obj.save()

            data['error_msg'] = ""
            data['success'] = "True"
            messages.success(request, "Order Status changed.")

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

            data['error_msg'] = ""
            data['success'] = "True"
            messages.success(request, "Order Status changed.")

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
        return HttpResponse(json.dumps(data), content_type='application/json')

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

    def post(self, request):
        data = {}
        django_messages = []
        try:            
            return HttpResponse(json.dumps(data), content_type='application/json')
        except:
            data['error_msg'] = "something went WRONG"
            return HttpResponse(json.dumps(data), content_type='application/json')