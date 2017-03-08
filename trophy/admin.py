__author__ = 'nibesh'

from django.contrib import admin
from .models import TrophyModel


class TrophyModelAdmin(admin.ModelAdmin):
    list_display = ('dealer', 'twilio_mobile', 'trophy', 'message', 'default_order_response', 'enabled')
    search_fields = ('dealer', 'twilio_mobile', 'trophy')


admin.site.register(TrophyModel, TrophyModelAdmin)
