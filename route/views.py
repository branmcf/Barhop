
from twilio import twiml

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET

from t_auth.models import RefNewUser, CustomUser
from trophy.models import TrophyModel
from managed_account.models import *

from block.models import BlockModel

from lib.utils import json_response, get_current_url
from lib.tw import send_new_user_message, send_message, send_multimedia_message

from route.forms import OrderReadyForm
from route.models import *
from route.utils import (parse_sms, get_user_by_mobile, get_trophy_by_twilio_mobile, get_ref_user_by_mobile, get_trigger_by_name, save_user_dealer_chat, check_grid_availability)
from ws4redis.redis_store import RedisMessage
from ws4redis.publisher import RedisPublisher
from django.conf import settings
from lib.bitly import shorten
from django.utils.crypto import get_random_string

@require_POST
@csrf_exempt
def handle_sms(request):
    
    """

    :param request:
    :return:
    """
    trigger = None
    SEND_ERROR = False
    vendor_number = settings.BARHOP_NUMBER
    from_, body = parse_sms(request.POST)

    try:
        location = request.POST['FromCity']
    except:
        location = ''

    from_ = '+919946341903'


    if body:
        body = str(body)
        if body.find('-') != -1:
            trigger = body.split('-')[1]
            trigger = trigger.strip()
            client_message = trigger
        else:
            trigger = body
            client_message = body

    #====== Checks text or number ==========
    checkType = RepresentsInt(client_message)
    if checkType:
        client_message_number = int(client_message)
    else:
        client_message_number = client_message
    #=======================================

    r = twiml.Response()

    # ====================================== #
    # Get Customer data using mobile number  #
    # ====================================== #
    customer = get_user_by_mobile(from_)
    ref_user_obj = get_ref_user_by_mobile(from_)

    # ============================================ #
    # Check if the user already has a conversation #
    # ============================================ #
    
    try:
        conversation = Conversation.objects.get(customer=customer, closed=False,)
    except:
        conversation = None

    if not conversation:

        trigger_data = get_trigger_by_name(trigger)

        # ================================================== #
        # here we have to notify the client that there is no 
        # such trigger name.
        # ================================================== #
        if trigger_data is None:
            message = 'This trigger name does not exist'
            send_message(vendor_number, from_, message)
            return HttpResponse(str(r))

        dealer = trigger_data.dealer

        try:
            trophy = TrophyModel.objects.get(dealer=dealer)
        except:
            trophy = None

        
        if customer is None:

            if ref_user_obj:
                # ================================================= #
                # Saving the current requested trigger for the user
                # ================================================= #
                ref_user_obj.current_trigger = trigger_data
                ref_user_obj.save()
                send_new_user_message(request, vendor_number, from_, ref_user_obj.id)
            else:
                ref_user = RefNewUser(dealer=dealer, dealer_mobile=vendor_number, mobile=from_, current_trigger=trigger_data)
                ref_user.save()
                #Send mail to user for signup
                send_new_user_message(request, vendor_number, from_, ref_user.id)

        else:            
            if customer.is_active:
                # ===================================================#
                # Saving the current requested trigger for the user #
                # =================================================#
                if ref_user_obj:
                    ref_user_obj.current_trigger = trigger_data
                    ref_user_obj.save()

                conversation = Conversation.objects.create(dealer=dealer, 
                    trigger=trigger_data, 
                    customer=customer, 
                    trophy=trophy,
                    process_stage=1)

                #==============================================#
                # Checking grid availability to place order   #
                # if grid full return a message to try again #
                #===========================================#                
                trigger_id = trigger_data.id
                grid_availability = check_grid_availability(trigger_id)

                if not grid_availability:
                    message_to_client = "Sorry, Too many orders in server. Please try after few minutes, Thank you."
                    message_recieved_dealer = trigger_data.trigger_name

                    save_user_dealer_chat(conversation,message_to_client, message_recieved_dealer)
                    send_message(vendor_number, from_, message_to_client)
                    conversation.closed = True
                    conversation.save()

                    return HttpResponse(str(r))

                #==============#
                # Menu list   #
                #============#
                try:
                    menu_image = MenuListImages.objects.get(trigger=trigger_data)
                    # menu_image = get_menu_image(trigger_data)
                    image_url = menu_image.image.url
                    url = get_current_url(request)
                    media_url = url+image_url
                    print("\n Media_url :"+str(media_url))
                except:
                    message_to_client = "Sorry for the inconvenience. No Menu added for this Bar. Thank you."
                    message_recieved_dealer = client_message

                    save_user_dealer_chat(conversation,message_to_client, message_recieved_dealer)
                    send_message(vendor_number, from_, message_to_client)
                    conversation.closed = True
                    conversation.save()
                    return HttpResponse(str(r))


                #************************************#
                # random number creation order_code #
                #**********************************#
                random_num = get_random_string(length=4, allowed_chars='QWERTYUIOP123ASDFGHJKL456ZXCVBNM7890')
                order_code = str(random_num)+str(conversation.id)
                purchaseOrder = PurchaseOrder.objects.create(order_code=order_code,
                    conversation=conversation,
                    dealer=dealer,
                    customer=customer,
                    trigger=trigger_data,
                    order_status='PENDING',
                    location = location
                    )

                message_to_client = "Welcome to Barhop! here is the menu for "+ str(trigger_data.trigger_name) +" Reply 'START' to start your order"
                message_recieved_dealer = client_message

                save_user_dealer_chat(conversation,message_to_client, message_recieved_dealer)
                send_multimedia_message(vendor_number, from_, message_to_client, media_url)                

            else:
                message = 'Your account is not active yet. Please activate your account by following link your in your email.'
                send_message(vendor_number, from_, message)
                return HttpResponse(str(r))

    else:
        trigger = conversation.trigger
        trigger_name = trigger.trigger_name
        process_stage = conversation.process_stage
        dealer = conversation.dealer
        customer = conversation.customer
        purchaseOrder = PurchaseOrder.objects.get(conversation=conversation)
        if not purchaseOrder.location:
            purchaseOrder.location = location
            purchaseOrder.save()

        if process_stage == 1 and client_message.lower() == "start" :                        
            message_to_client = "Text in the drink number of the first drink you want"
            message_recieved_dealer = client_message

            save_user_dealer_chat(conversation,message_to_client, message_recieved_dealer)
            send_message(vendor_number, from_, message_to_client)

            conversation.process_stage = 2
            conversation.save()

            #=================================#
            # Create an entry in order table #
            #===============================#

        elif process_stage == 2 and type(client_message_number) == int :

            #===========================#
            # Check menu item is valid #
            #=========================#
            try:
                menu_object = MenuItems.objects.get(id=client_message)
            except:
                menu_object = None

            if menu_object is None:
                message_to_client = "Invalid input. Please check Item number"
                message_recieved_dealer = client_message

                save_user_dealer_chat(conversation,message_to_client, message_recieved_dealer)                
                send_message(vendor_number, from_, message_to_client)
                return HttpResponse(str(r))
            
            #==================================#
            # Update menu item in order table #
            #================================#
            purchaseOrder = PurchaseOrder.objects.get(conversation=conversation,dealer=dealer,customer=customer,trigger=trigger,order_status='PENDING')

            order_menu_mapping = OrderMenuMapping.objects.create(order=purchaseOrder,
                menu_item=menu_object)

            message_to_client = "How many '"+ str(menu_object.item_name) +"' do you want?"
            message_recieved_dealer = client_message

            save_user_dealer_chat(conversation,message_to_client, message_recieved_dealer) 
            send_message(vendor_number, from_, message_to_client)

            conversation.process_stage = 3            
            conversation.save()

        elif process_stage == 3 and type(client_message_number) == int :

            
            if client_message_number > 0:

                #================================#
                # Update quantity in order table #
                #================================#
                purchaseOrder = PurchaseOrder.objects.get(conversation=conversation, dealer=dealer,customer=customer,trigger=trigger,order_status='PENDING')
                order_menu_mapping = OrderMenuMapping.objects.get(order=purchaseOrder)
                order_menu_mapping.quantity = client_message

                #=============================#
                # Toatal amount for each item #
                #=============================#
                price = order_menu_mapping.menu_item.item_price
                quantity = client_message
                total_amount = float(price) * float(quantity)

                order_menu_mapping.total_item_amount = total_amount
                order_menu_mapping.save()

                message_to_client = "Text in the drink number of the second drink you want or reply 'DONE' to checkout"
                message_recieved_dealer = client_message

                save_user_dealer_chat(conversation,message_to_client, message_recieved_dealer)
                send_message(vendor_number, from_, message_to_client)

                conversation.process_stage = 4 
                conversation.save()
            else:
                message_to_client = "Please enter a valid quantity."
                message_recieved_dealer = client_message

                save_user_dealer_chat(conversation,message_to_client, message_recieved_dealer)
                send_message(vendor_number, from_, message_to_client)

        elif process_stage == 4 and client_message.lower() == "done" :
            url = get_current_url(request)
            payment_url = str(url) +"/payment/purchase_invoice/"+str(purchaseOrder.id)
            url_shorten = shorten(payment_url)
            message_to_client = "Pay for your drinks here "+ str(url_shorten)
            message_recieved_dealer = client_message

            purchaseOrder = PurchaseOrder.objects.get(conversation=conversation, dealer=dealer, customer=customer,trigger=trigger,order_status='PENDING')
            order_menu_mapping = OrderMenuMapping.objects.filter(order=purchaseOrder)

            tottal_amount = 0
            for order_mapp in order_menu_mapping:
                
                #total amount 
                tottal_amount += order_mapp.total_item_amount

                #==================================#    
                #  Checking Item availability and  #
                #  Updating Item quantity          #
                #==================================#
                ordered_quantity = order_mapp.quantity
                item = MenuItems.objects.get(id=order_mapp.menu_item.id)

                available_quantity = item.quantity_available
                if available_quantity < ordered_quantity :
                    
                    # Updating conversation stage
                    conversation.process_stage = 3
                    conversation.save()
                    
                    message_to_client = "Sorry, your order is higher than available stock. Available quantity of " + str(item.item_name) +" is "+str(available_quantity)+ ". Please enter the number of quantity again."
                    message_recieved_dealer = client_message

                    save_user_dealer_chat(conversation,message_to_client, message_recieved_dealer)
                    send_message(vendor_number, from_, message_to_client)
                    return HttpResponse(str(r))
                else:
                    item.quantity_available = available_quantity - ordered_quantity
                    item.save()

            purchaseOrder.total_amount_paid = tottal_amount
            purchaseOrder.save()

            save_user_dealer_chat(conversation,message_to_client, message_recieved_dealer)
            send_message(vendor_number, from_, message_to_client)

            conversation.process_stage = 5
            conversation.save()

        elif process_stage == 4 and type(client_message_number) == int:

            # ========================= #
            # Check menu item is valid
            # ========================= #
            try:
                menu_object = MenuItems.objects.get(id=client_message)
            except:
                menu_object = None

            if menu_object is None:
                message_to_client = "Invalid input. Please check Item number"
                message_recieved_dealer = client_message

                save_user_dealer_chat(conversation,message_to_client, message_recieved_dealer)                
                send_message(vendor_number, from_, message_to_client)

                return HttpResponse(str(r))

            message_to_client = "How many '"+ str(menu_object.item_name) +"' do you want?"
            message_recieved_dealer = client_message

            save_user_dealer_chat(conversation,message_to_client, message_recieved_dealer) 
            send_message(vendor_number, from_, message_to_client)

            conversation.process_stage = 3            
            conversation.save()

        else:
            if process_stage == 5:
                message_to_client = "You have already one pending order to pay"
                message_recieved_dealer = client_message
                send_message(vendor_number, from_, message_to_client)
                save_user_dealer_chat(conversation,message_to_client, message_recieved_dealer)
                return HttpResponse(str(r))

            message_to_client = "Invalid message. Please send the correct message."
            message_recieved_dealer = client_message

            send_message(vendor_number, from_, message_to_client)
            save_user_dealer_chat(conversation,message_to_client, message_recieved_dealer)
            return HttpResponse(str(r))

    return HttpResponse(str(r))

def prettify_number(number):
    """

    :param number:
    :return:
    """
    a = number[-10:]
    return a[0:3] + '-' + a[3:6] + '-' + a[6:10]

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
