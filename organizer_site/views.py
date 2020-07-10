#import
from django.shortcuts import render , redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMessage, send_mail
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth.hashers import make_password, check_password
from django.template.loader import render_to_string
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.urls import reverse
from datetime import datetime
from django.conf import settings
import hashlib
import uuid
import json
import base64
from django.db.models import Q
import os

# import models
from django.contrib.auth.models import User
from event_management_proj.models import EventDetails, cashbackRecords, TktPurchaseDetails


from event_management_proj.views import getAllDistrict, HimachalDistrict
# ends here ~ import models


# check login User have right to access Organizer Dashboard
def isOrganizerUserLogin(request):
	try:
		if('user_id' in request.session):
			userId = request.session['user_id']
			userFilterData = User.objects.get(id=userId,is_superuser=False,is_active=True,is_staff=True)
			return userId
		else:
			return False
	except Exception as e:
		print('error in isOrganizerUserLogin function >> ',e)
		return False
# ends here ~  check login User have right to access Organizer Dashboard

# organizer dashboard funtion
def organizerDashboard(request):
	userId = isOrganizerUserLogin(request)
	if (userId == False):
		return HttpResponseRedirect(reverse('login'))

	# GET Method
	if request.method == 'GET':
		currentTime = datetime.now()

		# upcoming event count
		upEventCount = EventDetails.objects.filter(user_id=userId, tkt_end_datetime__gte=currentTime).count()
		# ends here ~ upcoming event count

		# count of total event created by current login organizer
		totalEventCount = EventDetails.objects.filter(user_id=userId, tkt_end_datetime__gte=currentTime).count()
		# ends here ~ count of total event created by current login organizer

		# count of expire event 
		expireEventCount = EventDetails.objects.filter(user_id=userId, tkt_end_datetime__lte=currentTime).count()
		# ends here ~ count of expire event 

		# list of id's of event which is created by current login organizer
		allEvtDtlFilter = EventDetails.objects.filter(user_id=userId).values('id')
		allEvtDtlIdsList = [ allEvt['id'] for allEvt in list(allEvtDtlFilter) ]
		# ends here ~ list of id's of event which is created by current login organizer

		# event id according to tickets which is user apply for cancel 
		pendingCbRecFilter = cashbackRecords.objects.filter(is_cashback_receive=False, event_id__in=allEvtDtlIdsList).values()
		pendingCbRecList = list(pendingCbRecFilter)
		# ends here ~ event id according to tickets which is user apply for cancel

		# event which is requested for cash back
		# eventDetailsFilter = EventDetails.objects.filter(user_id=userId, tkt_end_datetime__gte=currentTime, id__in=pendingCbRecList).values()
		# eventDetailsList = list(eventDetailsFilter)
		cancelReqCount = len(pendingCbRecFilter)
		# ends here ~ event which is requested for cash back

		return render(request, 'organizer_site/dashboard.html',{'upcoming_event_count':upEventCount,'total_event_count':totalEventCount,'expire_event_count':expireEventCount,'cancel_req_event_details':pendingCbRecFilter,'cancel_req_count':cancelReqCount})
	# ends here ~ GET Method
	
# ends here ~ organizer dashboard funtion

# function for add event
@csrf_exempt
def addEvent(request):
	userId = isOrganizerUserLogin(request)
	if (userId == False):
		return HttpResponseRedirect(reverse('login'))
	
	# GET Method
	if request.method == 'GET':
		himachalDistrictList = getAllDistrict()
		return render(request, 'organizer_site/add_event.html',{'himachal_district_list':himachalDistrictList,'mode':'add-event'})
	# ends here ~ GET Method

	# POST Method
	if request.method == 'POST':
		try:
			# read request data
			requestData = request.body
			requestDataDecode = requestData.decode('utf8').replace("'", '"')
			requestDataJson = json.loads(requestDataDecode)
			json_data = requestDataJson
			# ends here ~ read request data

			# set request data into variable
			venue = requestDataJson['venue']
			venue_district = requestDataJson['venue_district']
			event_start_datetime = requestDataJson['event_start_datetime']
			event_end_datetime = requestDataJson['event_end_datetime']
			tkt_start_datetime = requestDataJson['event_start_datetime']
			tkt_end_datetime = requestDataJson['event_end_datetime']
			# ends here ~ set request data into variable


			# change datetime format
			event_start_datetime = datetime.strptime(event_start_datetime, '%d-%m-%Y %I:%M %p')
			event_end_datetime = datetime.strptime(event_end_datetime, '%d-%m-%Y %I:%M %p')
			tkt_start_datetime = datetime.strptime(tkt_start_datetime, '%d-%m-%Y %I:%M %p')
			tkt_end_datetime = datetime.strptime(tkt_end_datetime, '%d-%m-%Y %I:%M %p')
			# ends here ~ change datetime format

			# reassing change data into dict
			json_data['event_start_datetime'] = event_start_datetime
			json_data['event_end_datetime'] = event_end_datetime
			json_data['tkt_start_datetime'] = tkt_start_datetime
			json_data['tkt_end_datetime'] = tkt_end_datetime
			json_data['user_id'] = userId
			# ends here ~  reassing change data into dict


			# check event is already exists or not
			# eventDetailsFilter = EventDetails.objects.filter(venue=venue,event_start_datetime__gte=event_start_datetime,event_end_datetime__lte=event_end_datetime)
			eventDetailsFilter = EventDetails.objects.filter(
				Q(venue=venue,event_start_datetime__range=(event_start_datetime,event_end_datetime))
				|Q(venue=venue,event_end_datetime__range=(event_start_datetime,event_end_datetime))
				|Q(venue=venue,event_start_datetime__lte=event_start_datetime,event_end_datetime__gte=event_end_datetime)
			)
			# ends here ~ check event is already exists or not

			if(len(eventDetailsFilter) == 0):
				filterHimachalDistrict = HimachalDistrict.objects.get(id=venue_district)
				json_data['venue_district'] = filterHimachalDistrict
				EventDetails.objects.create(**json_data)

				redirectUrl = reverse('organizer_site:list-event')
				messageData = {'responseType':'success', 'messageType':'success', 'message':'Event is Created Sucessfully.', 'responseData':[], 'nextPageUrl':str(redirectUrl), 'isRedirectNext':True}
				return HttpResponse(json.dumps(messageData))

			else:
				messageData = {'responseType':'success', 'messageType':'error', 'message':'Its seems like You are Creating Duplicate Event.', 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False}
				return HttpResponse(json.dumps(messageData))

		except Exception as e:
			print(' error in addEvent function >> ',e)
			messageData = {'responseType':'success', 'messageType':'error', 'message':'Something went wrong while Creating Event. Please try again after Refresh Page', 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False}
			return HttpResponse(json.dumps(messageData))


	# ends here ~ POST Method

# ends here ~ function for add event

# function for list all events created by user
def listEvent(request):
	userId = isOrganizerUserLogin(request)
	if (userId == False):
		return HttpResponseRedirect(reverse('login'))
	
	# GET Method
	if request.method == 'GET':
		currentTime = datetime.now()
		activeEventDetailsFilter = EventDetails.objects.filter(user_id=userId, tkt_end_datetime__gte=currentTime).values()
		activeEventDetails = list(activeEventDetailsFilter)

		return render(request, 'organizer_site/list_event.html',{'active_event_details':activeEventDetails})
	# ends here ~ GET Method

# ends here ~ function for list all events created by user

# function for edit event
@csrf_exempt
def editEvent(request, event_id):
	userId = isOrganizerUserLogin(request)
	if (userId == False):
		return HttpResponseRedirect(reverse('login'))

	try:
		# get event details according to id
		eventDetailsFilter = EventDetails.objects.filter(id=event_id, user_id=userId).values()
		# ends here ~ get event details according to id

		if(len(eventDetailsFilter) == 0):
			HttpResponseRedirect(reverse('organizer_site:add-event'))

		# GET Method
		if request.method == 'GET':
			himachalDistrictList = getAllDistrict()
			eventDetailsDict = list(eventDetailsFilter)[0]
			eventDetailsDict['tkt_price'] = int(eventDetailsDict['tkt_price'])
			event_long_desc = eventDetailsDict['event_long_desc']
			# del eventDetailsDict['event_long_desc']


			return render(request, 'organizer_site/edit_event.html',{'himachal_district_list':himachalDistrictList,'mode':'edit-event','event_detail':eventDetailsDict, 'event_long_desc':event_long_desc})
		# ends here ~ GET Method

		# POST Method
		if request.method == 'POST':
			# read request data
			requestData = request.body
			requestDataDecode = requestData.decode('utf8').replace("'", '"')
			requestDataJson = json.loads(requestDataDecode)
			json_data = requestDataJson
			# ends here ~ read request data

			# set request data into variable
			venue = requestDataJson['venue']
			venue_district = requestDataJson['venue_district']
			event_start_datetime = requestDataJson['event_start_datetime']
			event_end_datetime = requestDataJson['event_end_datetime']
			tkt_start_datetime = requestDataJson['event_start_datetime']
			tkt_end_datetime = requestDataJson['event_end_datetime']
			# ends here ~ set request data into variable


			# change datetime format
			event_start_datetime = datetime.strptime(event_start_datetime, '%d-%m-%Y %I:%M %p')
			event_end_datetime = datetime.strptime(event_end_datetime, '%d-%m-%Y %I:%M %p')
			tkt_start_datetime = datetime.strptime(tkt_start_datetime, '%d-%m-%Y %I:%M %p')
			tkt_end_datetime = datetime.strptime(tkt_end_datetime, '%d-%m-%Y %I:%M %p')
			# ends here ~ change datetime format

			# reassing change data into dict
			json_data['event_start_datetime'] = event_start_datetime
			json_data['event_end_datetime'] = event_end_datetime
			json_data['tkt_start_datetime'] = tkt_start_datetime
			json_data['tkt_end_datetime'] = tkt_end_datetime
			json_data['user_id'] = userId
			# ends here ~  reassing change data into dict


			# check event is already exists or not
			eventDetailsFilter = EventDetails.objects.filter(
				Q(venue=venue,event_start_datetime__range=(event_start_datetime,event_end_datetime))
				|Q(venue=venue,event_end_datetime__range=(event_start_datetime,event_end_datetime))
				|Q(venue=venue,event_start_datetime__lte=event_start_datetime,event_end_datetime__gte=event_end_datetime)
			).exclude(id=event_id)
			# ends here ~ check event is already exists or not


			if(len(eventDetailsFilter) == 0):
				filterHimachalDistrict = HimachalDistrict.objects.get(id=venue_district)
				json_data['venue_district'] = filterHimachalDistrict
				EventDetails.objects.filter(id=event_id).update(**json_data)

				redirectUrl = reverse('organizer_site:list-event')
				messageData = {'responseType':'success', 'messageType':'success', 'message':'Event is Updated Sucessfully.', 'responseData':[], 'nextPageUrl':str(redirectUrl), 'isRedirectNext':True}
				return HttpResponse(json.dumps(messageData))

			else:
				messageData = {'responseType':'success', 'messageType':'error', 'message':'Its seems like You are updating Invalid Event.', 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False}
				return HttpResponse(json.dumps(messageData))

		# ends here ~ POST Method

	except Exception as e:
		pass

# ends here ~ function for edit event


# function for upload and update event image
@csrf_exempt
def updateEventImg(request, event_id):
	try:
		userId = isOrganizerUserLogin(request)
		if (userId == False):
			return HttpResponseRedirect(reverse('login'))

		# GET Method
		if request.method == 'GET':
			eventDetails = EventDetails.objects.get(id=event_id)
			event_img = eventDetails.image
			return render(request, 'organizer_site/update_event_img.html',{'event_img':event_img, 'event_id':event_id})
		# ends here ~ GET Method

		# POST METHOD
		if request.method == 'POST':
			# read request data
			requestData = request.body
			requestDataDecode = requestData.decode('utf8').replace("'", '"')
			requestDataJson = json.loads(requestDataDecode)
			# ends here ~ read request data

			# set request data into variable
			image_data = requestDataJson['image_base_64']
			# ends here ~ set request data into variable

			# split base64 and set data into variable
			imgFormat, imgstr = image_data.split(';base64,')
			imgExt = imgFormat.split('/')[-1]
			imageData = ContentFile(base64.b64decode(imgstr))
			# ends here ~ split base64 and set data into variable
			
			# set unique file name
			file_name = str(uuid.uuid4())+'.'+imgExt
			file_name_with_path = '/event_images/'+ file_name
			full_filename = settings.MEDIA_ROOT + file_name_with_path
			# ends here ~ set unique file name

			# save file to directory
			file_name = default_storage.save(full_filename, imageData)
			# ends here ~ save file to directory

			eventDetails = EventDetails.objects.get(id=event_id)
			event_img = eventDetails.image

			if event_img != '':
				os.remove(settings.MEDIA_ROOT + event_img)			
			EventDetails.objects.filter(id=event_id).update(image=file_name_with_path)

			redirectUrl = reverse('organizer_site:list-event')
			messageData = {'responseType':'success', 'messageType':'success', 'message':'Image Updated Sucessfully.', 'responseData':[], 'nextPageUrl':str(redirectUrl), 'isRedirectNext':True}
			return HttpResponse(json.dumps(messageData))


	except Exception as e:
		print(' error in updateEventImg function >> ',e)
# ends here ~ function for upload and update event image

# function for delete event
@csrf_exempt
def deleteEvent(request):
	try:
		userId = isOrganizerUserLogin(request)
		if (userId == False):
			return HttpResponseRedirect(reverse('login'))

		if request.method == 'POST':
			# read request data
			requestData = request.body
			requestDataDecode = requestData.decode('utf8').replace("'", '"')
			requestDataJson = json.loads(requestDataDecode)
			# ends here ~ read request data

			event_id = requestDataJson['event_id']

			eventDetailsFilter = EventDetails.objects.filter(id=event_id,total_tkt_sales=0)

			if(len(eventDetailsFilter) == 1):
				eventDetails = EventDetails.objects.get(id=event_id)
				event_img = eventDetails.image

				if event_img != '':
					os.remove(settings.MEDIA_ROOT + event_img)
				
				EventDetails.objects.filter(id=event_id).delete()

				redirectUrl = reverse('organizer_site:list-event')
				messageData = {'responseType':'success', 'messageType':'success', 'message':'Event Delete Sucessfully.', 'responseData':[], 'nextPageUrl':str(redirectUrl), 'isRedirectNext':True}
				return HttpResponse(json.dumps(messageData))
			else:
				messageData = {'responseType':'success', 'messageType':'error', 'message':'SORRY! You can not delete this Event because Some Ticket of this Event is already Sale', 'responseData':[], 'nextPageUrl':str(redirectUrl), 'isRedirectNext':True}
				return HttpResponse(json.dumps(messageData))

	except Exception as e:
		pass
# ends here ~ function for delete event

# function for take descision of ticket cancel req
@csrf_exempt
def ticketCancelReq(request):
	try:
		userId = isOrganizerUserLogin(request)
		if (userId == False):
			return HttpResponseRedirect(reverse('login'))

		if request.method == 'POST':
			# read request data
			requestData = request.body
			requestDataDecode = requestData.decode('utf8').replace("'", '"')
			requestDataJson = json.loads(requestDataDecode)
			# ends here ~ read request data

			# set data into variable
			approve_cancel_req = requestDataJson['approve_cancel_req']
			ticket_id = requestDataJson['ticket_id']
			# ends here ~ set data into variable

			if approve_cancel_req == True:
				# send invoice email
				contactEmail = settings.CONTACT_EMAIL
				websiteUrl = settings.WEBSITE_URL
				replyToEmail = settings.REPLY_TO_EMAIL

				# get user details
				userObj = User.objects.get(id=userId)
				userFullname = userObj.first_name + ' ' + userObj.last_name
				userEmail = userObj.email
				# ends here ~ get user details

				# ticket details
				tktPurchDtlObj = TktPurchaseDetails.objects.get(id=ticket_id)
				event_id = tktPurchDtlObj.event_id
				amount_paid = tktPurchDtlObj.amount_paid
				amtRefund = amount_paid/2
				tkt_qty = tktPurchDtlObj.tkt_qty
				# ends here ~ ticket details

				# event details
				evtDtlObj = EventDetails.objects.get(id=event_id)
				event_name = evtDtlObj.event_name
				evtVenue = evtDtlObj.venue
				totalTktSales = evtDtlObj.total_tkt_sales
				# ends here ~ event details

				# update ticket quantity
				totalTktSales = totalTktSales - tkt_qty
				EventDetails.objects.filter(id=event_id).update(total_tkt_sales=totalTktSales)
				# ends here ~ update ticket quantity

				# update user request of cancel enrollment from event
				cashbackRecords.objects.filter(id=ticket_id).update(is_cashback_receive=True)
				
				subject = 'Your 50 Percent Payment is Refund in Your Bank Account | Event Management'
				email_from = settings.EMAIL_WITH_DISPLAY_NAME
				recipient_list = [userEmail]
				html_message = render_to_string('static/email_templates/ticket_cancel_detail.html',{
						'website_url':websiteUrl,
						'contact_email':contactEmail,
						'full_name':userFullname,
						'event_name': event_name,
						'refund_amount':amtRefund,
						'venue':evtVenue
					})
				msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': replyToEmail})
				msg.content_subtype = "html"
				msgSentStatus = msg.send(fail_silently=False)
				# ends here ~ send invoice email
			elif approve_cancel_req == False:
				cashbackRecords.objects.filter(id=ticket_id).delete()
			messageData = {'responseType':'success', 'messageType':'success', 'message':'Operation Performed Sucessfully', 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':True}
			return HttpResponse(json.dumps(messageData))

			print(approve_cancel_req,' >> ',ticket_id)

	except Exception as e:
		print(' error in ticketCancelReq fn >> ',e)
# ends here ~ function for take descision of ticket cancel req
