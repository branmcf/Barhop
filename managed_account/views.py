__author__ = 'nibesh'

from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

import stripe

from payment.models import PaymentModel

from .models import BankAccount, ManagedAccount
from .forms import BankAccountCreationForm, ManagedAccountCreationForm
from django.views.generic import TemplateView,CreateView, FormView, DetailView, View

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

class UsersView(TemplateView):
    template_name = "managed_account/users.html"

class BankingView(TemplateView):
    template_name = "managed_account/banking.html"

class GridView(TemplateView):
    template_name = "managed_account/grid.html"

class TriggersView(TemplateView):
    template_name = "managed_account/triggers.html"