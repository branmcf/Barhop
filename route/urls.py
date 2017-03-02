__author__ = 'nibesh'

from django.conf.urls import url

from . import views

urlpatterns = [
    url('^accept_sms/(?P<dealer_id>\+[0-9]+)/$', views.handle_sms, name='sms_forward'),
    url('^view_conversation/(?P<conversation_id>[0-9]+)/$', views.view_conversation, name='view_conversation'),
    url('^ajax_conversation/(?P<conversation_id>[0-9]+)/$', views.ajax_conversation, name='ajax_conversation'),
    url('^close_conversation/(?P<conversation_id>[0-9]+)/$', views.close_conversation, name='close_conversation'),
    url('^order_ready/$', views.order_ready, name='order_ready'),

]
