__author__ = 'nibesh'

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^process/$', views.process_payment, name='process'),
    url(r'^send_price/$', views.send_price, name='send_price'),

]
