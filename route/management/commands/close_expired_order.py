from django.core.management.base import BaseCommand
from django.utils import timezone
from managed_account.models import PurchaseOrder

class Command(BaseCommand):
    def handle(self, *args, **options):
        orders = PurchaseOrder.objects.all()

        for order in orders:
            expire_time = order.expires
            now = timezone.now()

            if expire_time < now :
                order.order_status = "EXPIRED"
                order.save()

                conversation = order.conversation
                conversation.closed = True
                conversation.save()



