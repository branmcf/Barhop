__author__ = 'nibesh'

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^get/(?P<o_id>[0-9]+)/$', views.get_trophy, name='get'),
    url(r'^add/$', views.add_trophy, name='add'),
    url(r'^edit/(?P<o_id>[0-9]+)/$', views.edit_trophy, name='edit'),
    url(r'^conversation/(?P<trophy_id>[0-9]+)/$', views.get_trophy_conversations, name='trophy_conversation'),
    url(r'^default_order_response/(?P<conversation_id>[0-9]+)/$', views.get_default_response, name='default_response'),
    url(r'^delete/(?P<o_id>[0-9]+)/$', views.delete_trophy, name='delete'),
    url('^search/$', views.search, name='search'),
    url('^purchase/(?P<number>\+[0-9]+)/$', views.purchase, name='purchase'),

]
