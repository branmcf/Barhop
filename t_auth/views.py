
import datetime

from django.http import Http404, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.core.files.images import get_image_dimensions
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth import logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
import stripe

from lib.tw import send_message
from lib.image_handler import is_image, is_valid_image, ProfileImageUploader

from t_auth import forms
from t_auth import utils

from django.contrib.auth import login,logout, authenticate, get_user_model
from django.contrib import messages

from t_auth.models import RefNewUser, CustomUser
from route.models import Conversation, Message
from trophy.models import TrophyModel
from t_auth.forms import LoginForm
from payment.models import ManagedAccountStripeCredentials
# added
from django.views.generic import TemplateView,CreateView, FormView, DetailView, View
stripe.api_key = settings.STRIPE_SECRET_KEY


def new_user_signup(request):
    form = forms.NewUserSignUpForm(request.POST or None)
    if request.method == 'POST':
        _id = int(request.POST['id'])
        if form.is_valid():
            try:
                o = RefNewUser.objects.get(pk=_id)
            except RefNewUser.DoesNotExist:
                raise Http404
            cleaned_data = form.cleaned_data
            u = CustomUser(mobile=o.mobile, username=cleaned_data['username'], email=cleaned_data['email'],
                           is_active=False, is_staff=False, is_ref_user=True)
            u.set_password(cleaned_data['password1'])
            u.save()
            utils.send_email_verification(request, u)
            return render(request, 'authentication/email_sent.html')
        return render(request, 'ref_user/new_register.html', {'form': form, 'id': _id})
    try:
        _id = int(request.GET.get('id'))
        RefNewUser.objects.get(pk=_id)
    except (RefNewUser.DoesNotExist, ValueError):
        raise Http404
    return render(request, 'ref_user/new_register.html', {'form': form, 'id': _id})


def sign_up(request):
    if request.method == 'POST':
        data = request.POST.copy()
        data['date_joined'] = datetime.date.today()
        data['last_login'] = datetime.datetime.now()
        form = forms.CustomUserCreationForm(data)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.is_dealer = True
            user.save()
            utils.send_email_verification(request, user)
            return render(request, 'authentication/email_sent.html')
        return render(request, 'authentication/Auth_register.html', {'form': form})
    form = forms.CustomUserCreationForm()
    return render(request, 'authentication/Auth_register.html', {'form': form})


@require_GET
def activate_account(request, uidb64=None, token=None,
                     token_generator=default_token_generator):
    UserModel = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and user.is_active is False and token_generator.check_token(user, token):
        
        if user.is_ref_user:

            user.is_active = True
            user.is_staff = False
            user.save()

            ref_user = RefNewUser.objects.get(mobile=user.mobile)
            dealer = ref_user.dealer

            try:
                trophy_data = TrophyModel.objects.get(dealer=dealer)
            except TrophyModel.DoesNotExist:
                return Http404

            c = Conversation(dealer=dealer, customer=user, trophy=trophy_data)
            c.save()

            m = Message(conversation=c, message=ref_user.trigger, date=ref_user.date, direction=True)
            m.save()
            message = 'Thanks for Signing Up.'

            reply = trophy_data.message
            message = reply
            m = Message(conversation=c, message=message, direction=False)
            m.save()
            send_message(settings.BARHOP_NUMBER, user.mobile, message)

        else:

            user.is_active = True
            user.is_staff = True
            user.is_dealer = True
            user.save()
            #For dealers only
            trohpy = TrophyModel(dealer=user, message=user.username, default_order_response="Thanks for ordering.", enabled=True).save()

            # acc = stripe.Account.create(country='US', managed=True)
            # ma = ManagedAccountStripeCredentials(dealer=user, account_user_id=acc['id'], publishable_key=acc['keys']['publishable'], secret_key=acc['keys']['secret'])
            # ma.save()

        return render(request, 'authentication/sign_up_successful.html')
    return render(request, 'authentication/invalid_link.html')

class LoginView(View):
    template_name = "authentication/Auth_login.html"
    
    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, self.template_name, {'form':form})

    def authenticate_user(self, username=None, password=None):
        
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'username': username}
        try:
            user = CustomUser.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except:
            return None

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = self.authenticate_user(username=username, password=password)
            if user:
                user = authenticate(username=user.username, password=password)
           	if user is not None and user.is_authenticated() and user.is_ref_user == False and user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/')
            	else:
                    messages.success(request, "Sorry, you are not a Authorized user.")
                    return render(self.request,self.template_name,{'form':form})
            else:
                messages.success(request, "Sorry, you are not a Authorized user.")
                return render(self.request,self.template_name,{'form':form})
        else:
            return render(self.request,self.template_name,{'form':form})

@csrf_exempt
@login_required
@require_POST
def profile_image_upload(request):
    form = forms.ProfileImageForm(request.POST, request.FILES)
    if form.is_valid():
        profile_image = request.FILES.get('file')
        if is_image(profile_image):
            w, h = get_image_dimensions(profile_image)
            valid, error_message = is_valid_image(200, 200, w, h)
        else:
            valid = False
            error_message = 'The uploaded file doesn\'t seem to be an Image.'
        if not valid:
            form.add_error('file', error_message)
            return utils.json_response(ok=False, errors=form.errors)

        uploader = ProfileImageUploader(profile_image, request.user.username)
        uploader.upload()
        uploaded_file = uploader.get_image_name()
        user = request.user
        user.profile_image = uploaded_file
        user.save()
        return utils.json_response(ok=True, image_path=uploaded_file)
    return utils.json_response(ok=False, errors=form.errors)


@login_required
def profile(request):
    """

    :param request:
    :return:
    """
    form = forms.MobileForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = request.user
            user.mobile = form.cleaned_data['mobile']
            user.save()
        return render(request, 'dealer/index.html', {'form': form})
    return render(request, 'dealer/index.html')


@login_required
def delete_account(request):
    """

    :param request:
    :return:
    """
    user = request.user
    auth_logout(request)
    user.delete()
    return redirect('/')


class ManagingMenuView(TemplateView):
    template_name = 'menu.html'

    """Returns the area wise data for the index page"""
    def get_context_data(self, **kwargs):
        context = super(ManagingMenuView, self).get_context_data(**kwargs)
        return context
