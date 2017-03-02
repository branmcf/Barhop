__author__ = 'nibesh'

from django.contrib import admin
from .models import RevenueModel


class RevenueModelAdmin(admin.ModelAdmin):
    """

    """
    list_display = ('dealer', 'transaction_amount', 'charge_amount', 'date')
    search_fields = ('dealer',)


admin.site.register(RevenueModel, RevenueModelAdmin)
