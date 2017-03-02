"""barhop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

from django.contrib import admin
from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import main

urlpatterns = [
    url(r'^$', main.index, name='index'),
    url(r'^how_it_works/$', main.how_it_works, name='how_it_works'),
    url(r'^about_us/$', main.about_us, name='about_us'),
    url(r'^contact_us/$', main.contact_us, name='contact_us'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('t_auth.urls')),
    url(r'^route/', include('route.urls', namespace='route')),
    url(r'^payment/', include('payment.urls', namespace='payment')),
    url(r'^trophy/', include('trophy.urls', namespace='trophy')),
    url(r'^block/', include('block.urls', namespace='block')),
    url(r'^account/', include('managed_account.urls', namespace='managed_account')),

]

urlpatterns += staticfiles_urlpatterns()
