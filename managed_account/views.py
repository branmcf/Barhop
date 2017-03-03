__author__ = 'nibesh'

from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import stripe

from payment.models import PaymentModel
from t_auth.models import CustomUser, DealerEmployeMapping
from trophy.models import TrophyModel
from .models import BankAccount, ManagedAccount
from .forms import BankAccountCreationForm, ManagedAccountCreationForm
from t_auth.forms import CustomUserCreationForm
from django.views.generic import TemplateView,CreateView, FormView, DetailView, View
from django.http import HttpResponse
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

class TriggersView(TemplateView):
    template_name = "managed_account/triggers.html"


class UsersView(FormView):
    template_name = "managed_account/users.html"
    form_class = CustomUserCreationForm

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        dealer = self.request.user
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
        context['form'] = form
        return self.render_to_response(context)

    def form_valid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = form
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        dealer = self.request.user

        # try :
        user = CustomUser(username=username, email=email, is_active=False, is_staff=False)
        user.set_password(password)
        user.save()

        trophy = TrophyModel.objects.get(dealer=dealer)

        DealerEmployeMapping(dealer=dealer, employe=user, trophy_model=trophy, is_active=True).save()
        # except:
        #     pass
        context['employe_list'] = DealerEmployeMapping.objects.filter(dealer=dealer, is_active=True)
        return self.render_to_response(context)

        # idea_obj = form.save()
        # idea_obj.status = '1'
        # idea_obj.save()

class DeleteEmployeView(View):

    def get_context_data(self, request, *args,**kwargs):
        context = super(DeleteEmployeView, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):    
        try:
            user_id = request.POST['data']
            CustomUser.objects.get(id=user_id).delete()
            message = "success"
            return HttpResponse(json.dumps({'success': 'True', 'error_msg': message}), content_type='application/json')
        except:
            message = "something went WRONG"
            return HttpResponse(json.dumps({'success': 'False', 'error_msg': message}), content_type='application/json')

class changePasswordView(View):

    def post(self, request):
        try:
            user = CustomUser.objects.get(id=request.POST['user_id'])
            user.set_password(request.POST['password2'])
            user.save()
            message = "success"
            return HttpResponse(json.dumps({'success': 'True', 'error_msg': message}), content_type='application/json')
        except:
            message = "something went WRONG"
            return HttpResponse(json.dumps({'success': 'True', 'error_msg': message}), content_type='application/json')