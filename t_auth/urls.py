
from django.conf.urls import url

from t_auth import views
from t_auth.views import LoginView

urlpatterns = [
    # url('^login/$', 'django.contrib.auth.views.login', {'template_name': 'authentication/Auth_login.html'},
    #     name='login'),
    url('^login/$', LoginView.as_view(), name='login'),
    url('^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
    
    url('^signup/$', views.sign_up, name='sign_up'),
    url('^register/$', views.new_user_signup, name='new_register'),
    url('^delete/$', views.delete_account, name='account_delete'),
    url('^profile/$', views.profile, name='profile'),
    url('^image/upload/$', views.profile_image_upload, name='image_upload'),
    url('^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate_account, name='account_activate'),
    url('^password_change/$', 'django.contrib.auth.views.password_change',
        {'template_name': 'authentication/password_change.html'},
        name='password_change'),
    url('^password_change/done/$', 'django.contrib.auth.views.password_change_done',
        {'template_name': 'authentication/password_change_done.html'}, name='password_change_done'),
    url('^password_reset/$', 'django.contrib.auth.views.password_reset',
        {'template_name': 'authentication/password_reset_form.html',
         'email_template_name': 'authentication/password_reset_email.html',
         'subject_template_name': 'authentication/password_reset_subject.txt'}, name='password_reset'),
    url('^password_reset/done/$', 'django.contrib.auth.views.password_reset_complete',
        {'template_name': 'authentication/password_reset_done.html'}, name='password_reset_done'),
    url('^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'template_name': 'authentication/password_reset_confirm.html'}, name='password_reset_confirm'),
    url('^reset/done/$', 'django.contrib.auth.views.password_reset_complete',
        {'template_name': 'authentication/password_change_done.html'}, name='password_reset_complete')
    # url('^dealer_menu_manage/$', ManagingMenuView.as_view(), name='profile'),
]
