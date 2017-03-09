__author__ = 'nibesh'

from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
import stripe

from django.contrib import messages
from payment.models import PaymentModel
from t_auth.utils import send_email_auth
from t_auth.models import CustomUser, DealerEmployeMapping
from trophy.models import TrophyModel
from .models import BankAccount, ManagedAccount, Trigger
from .forms import BankAccountCreationForm, ManagedAccountCreationForm, AddTriggerForm
from t_auth.forms import CustomUserCreationForm
from django.views.generic import TemplateView,CreateView, FormView, DetailView, View, DeleteView
from django.http import HttpResponse
from django.utils.decorators import method_decorator
import json

@login_required
def account_home(request):
    return render(request, 'managed_account/account_main.html')


@login_required
def add_bank_account(request):
    """
    :param request:
    :return:
    """
    user = request.user
    try:
        ma = ManagedAccount.objects.get(dealer=user)
    except ManagedAccount.DoesNotExist:
        return redirect(reverse('managed_account:create_account'))

    stripe_public_key = ma.public_key

    if request.method == 'POST':

        form = BankAccountCreationForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            cleaned_data['stripeToken'] = request.POST.get('stripeToken')

            b = BankAccount(dealer=user, **cleaned_data)
            b.save()
            return redirect(reverse('managed_account:list_account'))
        return render(request, 'managed_account/add_bank_account.html',
                      {'form': form, 'stripe_public_key': stripe_public_key})

    form = BankAccountCreationForm()
    return render(request, 'managed_account/add_bank_account.html',
                  {'form': form, 'stripe_public_key': stripe_public_key})


@login_required
def get_bank_accounts(request):
    """

    :param request:
    :return:
    """
    user = request.user
    bank_accounts = BankAccount.objects.filter(dealer=user)
    return render(request, 'managed_account/list_bank_accounts.html', {'accounts': bank_accounts})


@login_required
def create(request):
    """

    :param request:
    :return:
    """
    user = request.user
    try:
        ManagedAccount.objects.get(dealer=user)
    except ManagedAccount.DoesNotExist:
        pass
    else:
        return redirect('/accounts/profile/')

    form = ManagedAccountCreationForm(request.POST or None)
    if request.method == 'POST':
        form = ManagedAccountCreationForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            country = cleaned_data.get('country')
            stripe.api_key = settings.STRIPE_SECRET_KEY

            acc = stripe.Account.create(country=country, managed=True)
            ma = ManagedAccount(dealer=user, account_id=acc['id'], public_key=acc['keys']['publishable'],
                                secret_key=acc['keys']['secret'])
            ma.save()
            return redirect('/accounts/profile')

    return render(request, 'managed_account/create.html', {'form': form})


@login_required
def account_status(request):
    """

    :param request:
    :return:
    """
    user = request.user
    try:
        ma = ManagedAccount.objects.get(dealer=user)
    except ManagedAccount.DoesNotExist:
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

# class UsersView(TemplateView):
#     template_name = "managed_account/users.html"

class BankingView(TemplateView):
    template_name = "managed_account/banking.html"

class GridView(TemplateView):
    template_name = "managed_account/grid.html"

class TriggerView(FormView):
    model = Trigger
    form_class = AddTriggerForm
    template_name = 'managed_account/triggers.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super(TriggerView, self).get_context_data(**kwargs)
        context['trigger_data'] = Trigger.objects.filter(dealer=self.request.user)
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
        dealer = self.request.user
        obj = Trigger(trigger_name=trigger_name,dealer=dealer)
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
        return self.delete(*args, **kwargs)

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
        context['employe_list'] = DealerEmployeMapping.objects.filter(dealer=dealer, is_active=True)            
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
        dealer = self.request.user
        context['employe_list'] = DealerEmployeMapping.objects.filter(dealer=dealer, is_active=True)
        context['form'] = form
        return self.render_to_response(context)

    def form_valid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = form
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        dealer = self.request.user

        try :
            user = CustomUser(username=username, email=email, is_active=True, is_staff=False)
            user.set_password(password)
            user.save()
            trophy = TrophyModel.objects.get(dealer=dealer)
            DealerEmployeMapping(dealer=dealer, employe=user, trophy_model=trophy, is_active=True).save()

            # ------> mail to employe <------
            ip = self.request.META.get('REMOTE_ADDR')
            message_body = render_to_string('mail_template/mail_newEmploye.html',
                {'dealer_name': dealer.username,
                'ip':ip,
                'username': username,
                'password':password })
            subject = 'Bar-Hope'
            to_email = [email]
            send_email_auth(subject,message_body,to_email)
            #------------------------

        except:
            pass
        context['employe_list'] = DealerEmployeMapping.objects.filter(dealer=dealer, is_active=True)
        return self.render_to_response(context)

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
            messages.success(request, "Deleted Employe "+username)

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
            message_body = render_to_string('mail_template/mail_passwordchange.html',
                {'username': user.username,
                'password':password })
            subject = 'Password Change'
            to_email = [ user.email ]
            send_email_auth(subject,message_body,to_email)
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