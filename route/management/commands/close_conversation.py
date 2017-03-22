from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from managed_account.models import PurchaseOrder
from route.models import Conversation
from datetime import datetime, timedelta


class Command(BaseCommand):
    def handle(self, *args, **options):
        current_time = timezone.now()
        time_threshold = current_time - timedelta(minutes=30)
        conversations = Conversation.objects.filter(date__lt=time_threshold,closed=False)
        for conversation in conversations:
            pending = 'PENDING'
            try:
                order = PurchaseOrder.objects.get(conversation=conversation,order_status=pending)
            except PurchaseOrder.DoesNotExist:
                order = None

            if order:
                order.delete()

            conversation.closed = True
            conversation.save()
