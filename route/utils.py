__author__ = 'nibesh'

from trophy.models import TrophyModel
from t_auth.models import CustomUser, RefNewUser
from managed_account.models import Trigger, GridDetails
from route.models import Message

def parse_sms(req):
    """

    :param req:
    :return:
    """
    return req.get('From'), req.get('Body')


def get_user_by_mobile(mobile):
    """

    :param mobile:
    :return:
    """
    try:
        return CustomUser.objects.get(mobile=mobile)
    except CustomUser.DoesNotExist:
        return None


def get_trophy_by_twilio_mobile(twilio_mobile):
    """

    :param twilio_mobile:
    :return:
    """
    try:
        return TrophyModel.objects.get(twilio_mobile=twilio_mobile, enabled=True)
    except TrophyModel.DoesNotExist:
        return None


def get_ref_user_by_mobile(mobile):
    """

    :param mobile:
    :return:
    """
    try:
        return RefNewUser.objects.get(mobile=mobile)
    except RefNewUser.DoesNotExist:
        return None

def get_trigger_by_name(trigger):
    """

    :param trigger_name:
    :return:
    """
    try:
        return Trigger.objects.get(trigger_name=trigger)
    except Trigger.DoesNotExist:
        return None
def save_user_dealer_chat(conversation,message_to_client, message_recieved_dealer):
    """

    :param conversation:
    :param client_message:
    :param dealer_message:
    ::
    """
    msg_data = Message(conversation=conversation, message=message_to_client,  from_dealer=True, direction=True)
    msg_data.save()
    del msg_data
    msg_data = Message(conversation=conversation, message=message_recieved_dealer, from_client=True, direction=False)
    msg_data.save()

def check_grid_availability(trigger_id):
    """

    :param trigger_id:
    :param purchaseOrder:
    :return:
    """
    #==============================#
    # Checking Grid availability   #
    #==============================#
    try:
        trigger = Trigger.objects.get(id=trigger_id)
        grid = trigger.grid_trgger.all()[0]
        grid_detail_obj = GridDetails.objects.filter(grid=grid, is_active=False)
        grid_detail_count = grid_detail_obj.count()
    except:
        grid_detail_count = 0

    if grid_detail_count > 0 :
        # ================================ #
        # Finidng the least counter grid
        # ================================ #
        # counter_list = []
        # for grid_detail in grid_detail_obj:
        #     counter_list.append(grid_detail.grid_counter)
        # counter = min(counter_list)
        return True
    else:
        return False