__author__ = 'nibesh'

from django.conf.urls import url
from django.contrib.auth import views

from . import views as account_view
from .views import *

urlpatterns = [
    url(r'^account_status/$', account_view.account_status, name='account_status'),
    url(r'^users/$', UsersView.as_view(), name='user_view'),
    url(r'^banking/$', BankingView.as_view(), name='bank_view'),
    url(r'^grid/$', GridView.as_view(), name='grid_view'),
    url('^triggers/$', TriggerView.as_view(), name='triggers'),
    url(r'^edit_trigger/$', TriggerEditView.as_view(), name='edit_trigger'),
    url(r'^delete_trigger/(?P<pk>\d+)$', TriggerDeleteView.as_view(), name='delete_trigger'),
]
