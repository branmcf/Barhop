__author__ = 'nibesh'

from trophy.models import TrophyModel
from t_auth.models import CustomUser, RefNewUser


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
