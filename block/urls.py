
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<user_id>[0-9]+)/$', views.block_user, name='block'),
    url(r'^unblock/(?P<user_id>[0-9]+)/$', views.un_block_user, name='unblock'),
    url(r'^blocked_users/', views.list_blocked_users, name='blocked_users')

]
