__author__ = 'nibesh'

from django.db import models
from django.utils import timezone
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from t_auth.utils import phone_regex
# from lib import mails
from django.core.mail import send_mail

# from trophy.models import TrophyModel


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), max_length=30, unique=True,
                                help_text=_('Required. 30 characters or fewer. Letters, digits and '
                                            '@/./+/-/_ only.'),
                                validators=[
                                    validators.RegexValidator(r'^[\w.@+-]+$',
                                                              _('Enter a valid username. '
                                                                'This value may contain only letters, numbers '
                                                                'and @/./+/-/_ characters.'), 'invalid'),
                                ],
                                error_messages={
                                    'unique': _("A user with that username already exists."),
                                })

    email = models.EmailField(_('email address'), unique=True, blank=False, null=False)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    mobile = models.CharField(_('Mobile'), max_length=15, null=True, blank=True, validators=[phone_regex])

    is_ref_user = models.BooleanField(default=False)

    is_dealer = models.BooleanField(default=False)

    profile_image = models.CharField(max_length=50, default='default_avatar.png', blank=True)

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'User'

    def get_full_name(self):
        """

        :return:
        """
        return self.username

    def get_short_name(self):
        """

        :return:
        """
        return self.username

    def __unicode__(self):
        """

        :return:
        """
        return self.username

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def email_user(self, subject, message, from_email=None):
        """
        :param subject:
        :param message:
        :param from_email:
        :return:
        """
        send_mail(subject, message, from_email, [self.email])

class RefNewUser(models.Model):
    """
    New Numbers are stored here first.
    """
    dealer = models.ForeignKey(CustomUser, related_name='user_creator')
    dealer_mobile = models.CharField(max_length=15)
    mobile = models.CharField(max_length=15)
    trigger = models.CharField(max_length=30)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'new_user'

class DealerEmployeMapping(models.Model):
    dealer = models.ForeignKey(CustomUser, related_name='dealer_mapping')
    employe = models.ForeignKey(CustomUser, related_name='employee_mapping')
    created_by = models.ForeignKey(CustomUser, related_name='user_created_by')
    trophy_model = models.ForeignKey('trophy.TrophyModel')
    is_active = models.BooleanField(_('active'), default=True)

