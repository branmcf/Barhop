from django.db import models
from django.utils import timezone

from t_auth.models import CustomUser
from django.utils.translation import ugettext_lazy as _
from picklefield.fields import PickledObjectField

ORDER_CHOICES = (
    ('PENDING', _('Pending')),
    ('PAID', _('Paid')),
    ('EXPIRED', _('Expired')),
    ('READY', _('Ready')),
    ('CLOSED', _('Closed')),
)


class Trigger(models.Model):
    dealer = models.ForeignKey(CustomUser, related_name='trigger_dealer')
    trigger_name = models.CharField(max_length=250, unique=True)
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, related_name='trigger_created_by')

    def __str__(self):
        return self.trigger_name

    class Meta:
        db_table = 'trigger'
        verbose_name = 'Trigger'
        verbose_name_plural = 'Triggers'

class MenuItems(models.Model):
    dealer = models.ForeignKey(CustomUser)
    item_name = models.CharField(max_length=800, null=True, blank=True)
    item_price = models.FloatField(default=0, null=True, blank=True)
    quantity_available = models.PositiveIntegerField(default=0, blank=True, null=True)
    created_by = models.ForeignKey(CustomUser, related_name='menu_created_by', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.item_name)

    class Meta:
        db_table = 'MenuItems'
        verbose_name = 'MenuItem'
        verbose_name_plural = 'MenuItems'


from route.models import Conversation
class PurchaseOrder(models.Model):
    order_code = models.CharField(max_length=250, unique=True, blank=True, null=True)
    conversation = models.ForeignKey(Conversation,related_name="order_conversation",blank=True, null=True)
    dealer = models.ForeignKey(CustomUser, related_name = "purchase_order_dealer", blank=True, null=True)
    customer = models.ForeignKey(CustomUser, related_name = "purchase_order_customer", blank=True, null=True)
    trigger = models.ForeignKey(Trigger,blank=True, null=True)
    order_status = models.CharField(_('Status'), choices=ORDER_CHOICES, max_length=10)
    total_amount_paid = models.FloatField(blank=True, null=True)
    created = models.DateTimeField(auto_now=True)
    expires = models.DateTimeField(blank=True, null=True)
    ip_address = models.FloatField(blank=True, null=True)
    location = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.order_code

    class Meta:
        db_table = 'PurchaseOrder'
        verbose_name = 'PurchaseOrder'
        verbose_name_plural = 'PurchaseOrders'

class OrderMenuMapping(models.Model):
    order = models.ForeignKey(PurchaseOrder, related_name = "order_menu_datar", blank=True, null=True)
    menu_item = models.ForeignKey(MenuItems, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0, blank=True, null=True)
    total_item_amount = models.FloatField(blank=True, null=True)

    def __str__(self):
        return str(self.order)

    class Meta:
        db_table = 'OrderMenuMapping'
        verbose_name = 'OrderMenuMapping'
        verbose_name_plural = 'OrderMenuMappings'



class Grid(models.Model):
    dealer = models.ForeignKey(CustomUser,blank=True, null=True)
    trigger = models.ForeignKey(Trigger,blank=True, null=True, related_name="grid_trgger")
    grid_row = models.PositiveIntegerField(default=0, blank=True, null=True)
    grid_column = models.PositiveIntegerField(default=0, blank=True, null=True)
    created_by = models.ForeignKey(CustomUser, related_name="created_employee",blank=True, null=True)

    def __str__(self):
        return str(self.trigger)

    class Meta:
        db_table = 'Grid'
        verbose_name = 'Grid'
        verbose_name_plural = 'Grids'

class GridDetails(models.Model):
    grid = models.ForeignKey(Grid, related_name="grid_details")
    order = models.ForeignKey(PurchaseOrder, blank=True, null=True, related_name="order_grid_detail")
    created = models.DateTimeField(auto_now=True)
    grid_counter = models.PositiveIntegerField(default=0, blank=True, null=True)
    location = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.grid)

    class Meta:
        db_table = 'GridDetails'
        verbose_name = 'GridDetails'
        verbose_name_plural = 'GridDetails'

class MenuListImages(models.Model):
    dealer = models.ForeignKey(CustomUser,blank=True, null=True)
    trigger = models.ForeignKey(Trigger,blank=True, null=True)
    image = models.FileField(upload_to='MenuImages/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class MenuCustomerMappping(models.Model):
    trigger = models.ForeignKey(Trigger, related_name="tigger_menu_map", blank=True, null=True)
    dealer = models.ForeignKey(CustomUser,related_name="dealer_menu_map", blank=True, null=True)
    customer = models.ForeignKey(CustomUser,related_name="customer_menu_map", blank=True, null=True)
    menu_data = PickledObjectField()