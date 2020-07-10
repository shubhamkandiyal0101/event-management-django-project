from django.db import models
from datetime import datetime

# model for himachal district
class HimachalDistrict(models.Model):
    district_val = models.CharField(max_length=100,default='',null=False)
    district_name = models.CharField(max_length=100,default='',null=False)


# token table model for various purpose
class ManualTokenStorage(models.Model):
    token = models.CharField(max_length=150,default='',null=False)
    generate_date = models.DateTimeField(null=True)
    token_expire_dt = models.DateTimeField(null=True)
    token_purpose = models.CharField(max_length=100,default='',null=False)
    email = models.CharField(max_length=100,default='',null=False)
# ends here ~ token table model for various purpose

# table for event details
class EventDetails(models.Model):
	event_name = models.CharField(max_length=100,default='',null=False)
	event_short_desc = models.CharField(max_length=500,default='',null=False)
	event_long_desc = models.CharField(max_length=1500,default='',null=False)
	image = models.CharField(max_length=300,default='',null=False)
	venue = models.CharField(max_length=300,default='',null=False)
	pincode = models.CharField(max_length=6,default='',null=False)
	venue_district = models.ForeignKey(HimachalDistrict, blank=False, null=False, on_delete=models.CASCADE)
	event_start_datetime = models.DateTimeField(null=True)
	event_end_datetime = models.DateTimeField(null=True)
	tkt_start_datetime = models.DateTimeField(null=True)
	tkt_end_datetime = models.DateTimeField(null=True)
	total_tkt_qty = models.IntegerField(default=0)
	tkt_price = models.FloatField(default=0)
	total_tkt_sales = models.IntegerField(default=0)
	date_added = models.DateTimeField(null=True)
	date_modified = models.DateTimeField(null=True)
	user_id = models.IntegerField(default=0)
# ends here ~ table for event details

# table for ticket purchase
class TktPurchaseDetails(models.Model):
	event_id = models.IntegerField(default=0)
	purch_by_user_id = models.IntegerField(default=0)
	purch_date = models.DateTimeField(null=True)
	tkt_qty = models.IntegerField(default=0)
	payment_id = models.CharField(max_length=50,default='',null=False)
	payment_request_id = models.CharField(max_length=50,default='',null=False)
	invoice_number = models.CharField(max_length=50,default='',null=False)
	amount_paid = models.FloatField(null=False,default=0)
# ends here ~ table for ticket purchase

# table for maintain cashback records
class cashbackRecords(models.Model):
	tkt_purch_id = models.IntegerField(default=0)
	event_id = models.IntegerField(default=0)
	user_id = models.IntegerField(default=0)
	is_cashback_receive = models.BooleanField(default=False)
# ends here ~ table for maintain cashback records
 





################################
# INITIAL DATA
################################

#################################################################
# def insertDistrict():
# 	himachalDistrictList = [
# 		{'district_val':'bilaspur', 'district_name':'Bilaspur'},
# 		{'district_val':'chamba', 'district_name':'Chamba'},
# 		{'district_val':'hamirpur', 'district_name':'Hamirpur'},
# 		{'district_val':'kangra', 'district_name':'Kangra'},
# 		{'district_val':'kinnaur', 'district_name':'Kinnaur'},
# 		{'district_val':'kullu', 'district_name':'Kullu'},
# 		{'district_val':'mandi', 'district_name':'Mandi'},
# 		{'district_val':'shimla', 'district_name':'Shimla'},
# 		{'district_val':'solan', 'district_name':'Solan'},
# 		{'district_val':'una', 'district_name':'Una'},
# 		{'district_val':'lahaul_spiti', 'district_name':'Lahaul & Spiti'},
# 		{'district_val':'sirmaur', 'district_name':'Sirmaur (Sirmour)'}
# 	]

# 	for data in himachalDistrictList:
# 		HimachalDistrict.objects.create(**data)
# 		print(' Successfully Inserted District Data ')
# insertDistrict()
####################################################################