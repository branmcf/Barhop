
# ================================================================= #
# Conjob to close a conversation if the user doesn't respond for
# more than 30 minutes .
# ================================================================= #



from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from managed_account.models import PurchaseOrder,OrderMenuMapping,MenuItems
from route.models import Conversation
from datetime import datetime, timedelta


class Command(BaseCommand):

    def handle(self, *args, **options):

        current_time = timezone.now()
        time_threshold = current_time - timedelta(seconds=10)
        conversations = Conversation.objects.filter(date__lt=time_threshold,closed=False)

        for conversation in conversations:
            pending = 'PENDING'

            try:
                order = PurchaseOrder.objects.get(conversation=conversation,order_status=pending)

                # update MenuItems
                orderMenuMappings = OrderMenuMapping.objects.filter(order=order)

                for mapping in orderMenuMappings:
                    quantity = mapping.quantity
                    menu_item = mapping.menu_item
                    new_quantity = menu_item.quantity_available + quantity
                    menuItemObj = MenuItems.objects.get(id=menu_item.id)
                    menuItemObj.quantity_available = new_quantity
                    menuItemObj.save()

            except PurchaseOrder.DoesNotExist:
                order = None

            if order:
                order.delete()

            conversation.closed = True
            conversation.save()
