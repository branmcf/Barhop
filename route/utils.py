__author__ = 'nibesh'

from trophy.models import TrophyModel
from t_auth.models import CustomUser, RefNewUser
from managed_account.models import Trigger, GridDetails, MenuListImages, MenuItems
from route.models import Message
import imgkit
from django.core.files import File

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

def get_menu_image(trigger_data):
    try:
        trigger_name = trigger_data.trigger_name
        dealer = trigger_data.dealer

        html = "<html><body style='color:red;'><div style='width:60%;margin:10% auto;'><table style='width:100%;color:#191919;' border=1><h2 style='color:#191919;'>"+ str(trigger_name) +"</h2><tr><th style='width:20%;background-color:#191919;color:#c1c1c1;'>Item Number</th><th style='background-color:#191919;color:#c1c1c1;'>Name</th><th style='width:20%;background-color:#191919;color:#c1c1c1;'>Price</th></tr>"

        menu_list = MenuItems.objects.filter(dealer=dealer)
        
        for menu in menu_list:
            if menu.quantity_available > 0 and menu.item_price > 0:
                html += "<tr><td style='padding-left:10px;'>"+str(menu.id)+"</td><td style='padding-left:10px;'>"+str(menu.item_name)+"</td><td style='padding-left:10px;'>"+str(menu.item_price)+"</td></tr>"
        
        html += "</table></div></body></html>"

        Html_file= open("test.html","w")
        Html_file.write(html)
        Html_file.close()

        try:
            imgkit.from_file('test.html', 'out.jpg')
        except:
            #pass imgkit exception
            pass
        file = open('out.jpg')
        image_file = File(file)
        image_obj, created = MenuListImages.objects.get_or_create(trigger=trigger_data, dealer=dealer)
        image_obj.image = image_file
        image_obj.save()
        return image_obj
    except:
        return False