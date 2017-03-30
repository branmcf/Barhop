__author__ = 'nibesh'

from django.conf.urls import url

from . import views
from .views import PaymentInvoiceView, PaymentSuccessView, PasswordAuthentication

urlpatterns = [
    url(r'^process/$', views.process_payment, name='process'),
    url(r'^send_price/$', views.send_price, name='send_price'),
    url(r'^purchase_invoice/(?P<pk>\d+)$', PaymentInvoiceView.as_view(), name='payment_invoice'),
    url(r'^payment_success/(?P<bill_num>[\w\-]+)$', PaymentSuccessView.as_view(), name='payment_success'),
    url(r'^user_Authentication/$', PasswordAuthentication.as_view(), name='password_auth')
]
