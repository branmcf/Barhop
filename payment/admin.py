__author__ = 'nibesh'

from django.contrib import admin
from .models import RevenueModel, PaymentModel,BankAccount


class RevenueModelAdmin(admin.ModelAdmin):
    """

    """
    list_display = ('dealer', 'transaction_amount', 'charge_amount', 'date')
    search_fields = ('dealer',)


admin.site.register(RevenueModel, RevenueModelAdmin)

class PaymentModelAdmin(admin.ModelAdmin):
    """

    """
    list_display = ('dealer', 'order', 'customer','total_amount', 'payment_date')
    search_fields = ('dealer',)


admin.site.register(PaymentModel, PaymentModelAdmin)
admin.site.register(BankAccount)