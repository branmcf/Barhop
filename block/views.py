__author__ = 'nibesh'

from django.utils import timezone
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

from lib.utils import json_response

from t_auth.models import CustomUser

from block.models import BlockModel


@require_GET
@login_required
def block_user(request, user_id):
    user = request.user
    try:
        blocked_user = CustomUser.objects.get(pk=user_id)
        b = BlockModel.objects.get(blocker=user, blocked_user=blocked_user)
        b.enabled = True
        b.date = timezone.now()
        b.save()
    except CustomUser.DoesNotExist:
        return json_response(success=False, message='Invalid request.')
    except BlockModel.DoesNotExist:
        b = BlockModel(blocker=user, blocked_user=blocked_user)
        b.save()
    return json_response(success=True, message='User Blocked')


@require_GET
@login_required
def un_block_user(request, user_id):
    user = request.user
    try:
        blocked_user = CustomUser.objects.get(pk=user_id)
        b = BlockModel.objects.get(blocker=user, blocked_user=blocked_user)
        b.enabled = False
        b.save()
    except CustomUser.DoesNotExist:
        return json_response(success=False, message='Invalid Request')
    return json_response(success=True, message='User UnBlocked')


@login_required
def list_blocked_users(request):
    user = request.user
    blocked_users = BlockModel.objects.filter(blocker=user)
    return