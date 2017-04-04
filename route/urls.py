
from django.conf.urls import url

from . import views

urlpatterns = [
    url('^accept_sms/$', views.handle_sms, name='sms_forward'),
]
