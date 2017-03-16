
from t_auth.models import CustomUser, DealerEmployeMapping

# return dealer of logged in user
def get_dealer(user):
	if user.is_dealer:
		dealer = user
	else:
		user_mapping_obj = DealerEmployeMapping.objects.get(employe=user)
		dealer = user_mapping_obj.dealer
	return dealer