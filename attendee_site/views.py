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
import requests

# import models
from django.contrib.auth.models import User
from event_management_proj.models import EventDetails, TktPurchaseDetails, cashbackRecords
from event_management_proj.views import getAllDistrict, HimachalDistrict
# ends here ~ import models

# check login User have right to access attendee Dashboard
def isAttendeeUserLogin(request):
	try:
		if('user_id' in request.session):
			userId = request.session['user_id']
			userFilterData = User.objects.get(id=userId,is_superuser=False,is_active=True,is_staff=False)
			return userId
		else:
			return False
	except Exception as e:
		print('error in isOrganizerUserLogin function >> ',e)
		return False
# ends here ~  check login User have right to access attendee Dashboard

# attendee dashboard funtion
def attendeeDashboard(request):
	userId = isAttendeeUserLogin(request)
	if (userId == False):
		return HttpResponseRedirect(reverse('login'))

	# GET Method
	if request.method == 'GET':
		currentTime = datetime.now()

		alreadyCbRecFilter = cashbackRecords.objects.filter(user_id=userId,is_cashback_receive=True).values('tkt_purch_id')
		if(len(alreadyCbRecFilter) > 0):
			alreadyCbRecList = [ cb['tkt_purch_id'] for cb in list(alreadyCbRecFilter) ]
		else:
			alreadyCbRecList = []

		tktPurchIdFilter = TktPurchaseDetails.objects.filter(purch_by_user_id=userId).exclude(id__in=alreadyCbRecList).values('event_id')

		if (len(tktPurchIdFilter) != 0):
		
			# total purchase ticket event id's list
			tktPurchIdList = [ tkt['event_id'] for tkt in list(tktPurchIdFilter) ] 
			# ends here ~ total purchase ticket event id's list
			
			# total enroll event
			enrollEvtCount = len(tktPurchIdList) 
			# ends here ~ total enroll event
			
			# upcoming event enroll values and count
			upEventDetailsFilter = EventDetails.objects.filter(id__in=tktPurchIdList,tkt_end_datetime__gte=currentTime).values()
			upEventDetailsList = list(upEventDetailsFilter)
			upcomingEvtEnrollCount = len(upEventDetailsList)
			# ends here ~ upcoming event values and countt

			# expired event enroll count
			expiredEvtEnrollCount = EventDetails.objects.filter(id__in=tktPurchIdList,tkt_end_datetime__lte=currentTime).count()
			# ends here ~ expired event enroll count

			cancelledEvtCount = len(alreadyCbRecFilter)

			pendingCbRecFilter = cashbackRecords.objects.filter(user_id=userId,is_cashback_receive=False).values('event_id')
			pendingCbRecList = [ cb['event_id'] for cb in list(pendingCbRecFilter) ]


		else:
			enrollEvtCount = 0
			upcomingEvtEnrollCount = 0
			expiredEvtEnrollCount = 0
			cancelledEvtCount = 0
			upEventDetailsList = []
			pendingCbRecList = []



		return render(request, 'attendee_site/dashboard.html',{'enroll_evt_count':enrollEvtCount, 'upcoming_evt_enroll_count':upcomingEvtEnrollCount,'expired_evt_enroll_count':expiredEvtEnrollCount,'cancelled_evt_count':cancelledEvtCount,'upcoming_event_details':upEventDetailsList,'pending_cb_id_rec_list':pendingCbRecList})
	# ends here ~ GET Method
	
# ends here ~ attendee dashboard funtion

# function for event list with some filters
def eventList(request, page_number):
	try:
		userId = isAttendeeUserLogin(request)
		if (userId == False):
			return HttpResponseRedirect(reverse('login'))

		tktPurchDetailsFilter = TktPurchaseDetails.objects.filter(purch_by_user_id=userId).values('event_id')
		purchTktEvtIdList = [ tkt['event_id'] for tkt in list(tktPurchDetailsFilter) ]

		eventDetailsCount = EventDetails.objects.all().exclude(id__in=purchTktEvtIdList).count()
		paginated_by = 5
		paginated_start = (page_number * paginated_by) - paginated_by
		paginated_end = (page_number * paginated_by) 
		
		if((type(page_number) != int) or (page_number == 0) or (((page_number*paginated_by) - eventDetailsCount) >= paginated_by)):
			return HttpResponseRedirect(reverse('attendee_site:attendee-dashboard'))

		# GET Request
		if request.method == 'GET':
			currentTime = datetime.now()
			eventDetailsFilter = EventDetails.objects.filter(tkt_end_datetime__gte=currentTime).exclude(id__in=purchTktEvtIdList)[paginated_start:paginated_end].values()

			eventDetailsList = list(eventDetailsFilter)

			remainingEventCount = eventDetailsCount - (page_number*paginated_by)
			previousPageNum = page_number - 1
			nextPageNum = page_number + 1
			
			return render(request, 'attendee_site/list_event.html',{'active_event_details':eventDetailsList, 'page_number':page_number, 'remaining_event_count':remainingEventCount, 'prev_page_num':previousPageNum, 'next_page_num':nextPageNum})
		# ends here ~ GET Request

	except Exception as e:
		print(' >> error in eventList fn >> ',e)
# ends here ~ function for event list with some filters

# function for buy ticket for event
@csrf_exempt
def buyTicket(request, event_id):
	try:
		userId = isAttendeeUserLogin(request)
		if (userId == False):
			return HttpResponseRedirect(reverse('login'))

		# GET Method
		if request.method == 'GET':
			currentTime = datetime.now()
			eventDetailsFilter = EventDetails.objects.filter(tkt_end_datetime__gte=currentTime,id=event_id).values()

			if(len(eventDetailsFilter) == 1):
				eventDetailDict = list(eventDetailsFilter)[0]

				total_tkt_qty = eventDetailDict['total_tkt_qty']
				total_tkt_sales = eventDetailDict['total_tkt_sales']
				tktQtyLeft = total_tkt_qty - total_tkt_sales

				if tktQtyLeft > 0:
					return render(request, 'attendee_site/buy_ticket.html',{'event_id':event_id, 'event_detail':eventDetailDict, 'tkt_qty_left':tktQtyLeft})
				else:
					return render(request, 'event_expired_invalid.html')

			else:
				return render(request, 'event_expired_invalid.html')
		# ends here ~ GET Method

		# POST Method
		if request.method == 'POST':
			# read request data
			requestData = request.body
			requestDataDecode = requestData.decode('utf8').replace("'", '"')
			requestDataJson = json.loads(requestDataDecode)
			# ends here ~ read request data

			userObject = User.objects.get(id=userId)

			# set request data into variables
			first_name = userObject.first_name
			last_name = userObject.last_name
			email = userObject.email
			fullName = first_name + ' ' + last_name
			eventId = requestDataJson['event_id']	
			tkt_qty = requestDataJson['ticketQty']	
			tkt_qty = int(tkt_qty)
			paymentPurpose=eventId+','+str(tkt_qty)+','+str(userId)
			# ends here ~ set request data into variables

			# other required varaibles
			hostUrl = request.META['HTTP_ORIGIN']
			mojoRedirectUrl = str(hostUrl)+'/attendee/event-payment-success'
			MOJO_API_KEY = settings.MOJO_API_KEY
			MOJO_AUTH_TOKEN = settings.MOJO_AUTH_TOKEN
			MOJO_PAYMENT_URL_HOST = settings.MOJO_PAYMENT_URL_HOST
			apiUrl = str(MOJO_PAYMENT_URL_HOST)+'/api/1.1/payment-requests/'
			# ends here ~ other required varaibles

			# Get Price of Event
			eventDetailObj = EventDetails.objects.get(id=eventId)
			singleTktPrc = eventDetailObj.tkt_price
			allTktPrc = singleTktPrc*tkt_qty
			# Ends here ~ Get Price of Event

			finalPaymentAmt = allTktPrc

			# call instamojo api to generate payment request
			# NOTE: Here PURPOSE (purpose) is using for Event ID and Ticket Quantity 
			headers = { "X-Api-Key": MOJO_API_KEY, "X-Auth-Token": MOJO_AUTH_TOKEN}
			payload = {
			  'purpose': paymentPurpose,
			  'amount': finalPaymentAmt,
			  'buyer_name': fullName,
			  'email': email,
			  'redirect_url': mojoRedirectUrl,
			  'send_email': 'True',
			  'webhook': '',
			  'allow_repeated_payments': 'True',
			}
			response = requests.post(apiUrl, data=payload, headers=headers)
			jsonResponse = json.loads(response.text)
			responseStatus = jsonResponse['success']
			# ends here ~ call instamojo api to generate payment request

			# code works according to responseStatus (payment gateway response) variable
			if(responseStatus == True):
				paymentUrl = jsonResponse['payment_request']['longurl']
				redirectUrl = paymentUrl
				messageData = {'responseType':'success', 'messageType':'success', 'message':'Thanks for Showing Interest in Event. Redirect You to Payment Page', 'responseData':[], 'nextPageUrl':str(redirectUrl), 'isRedirectNext':True}
				return HttpResponse(json.dumps(messageData))
			elif(responseStatus == False):
				errorMsg = jsonResponse['message']
				errorMsgStr = str(errorMsg)
				messageData = {'responseType':'success', 'messageType':'error', 'message':errorMsgStr, 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False}
				return HttpResponse(json.dumps(messageData))
			# ends here ~ code works according to responseStatus (payment gateway response) variable



		# ends here ~ POST Method
	except Exception as e:
		print(' error in buyTicket function >> ',e)
		messageData = {'responseType':'success', 'messageType':'error', 'message':'Something went wrong. Sorry for inconvenience', 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False}
		return HttpResponse(json.dumps(messageData))
# ends here ~ function for buy ticket for event

# function works when instamojo sends payment (success or failed) response from (instamojo) server after making payment
def eventPaymentSuccess(request):
	try:
		# read request data (payment response data) 
		requestDict = request.GET
		paymentRespDict = dict(requestDict)
		payment_id = paymentRespDict['payment_id'][0]
		payment_request_id = paymentRespDict['payment_request_id'][0]
		payment_status = paymentRespDict['payment_status'][0]
		# ends here ~ read request data (payment response data)

		# other required varaibles
		MOJO_API_KEY = settings.MOJO_API_KEY
		MOJO_AUTH_TOKEN = settings.MOJO_AUTH_TOKEN
		MOJO_PAYMENT_URL_HOST = settings.MOJO_PAYMENT_URL_HOST
		# ends here ~ other required varaibles

		# call instamojo api to get payment details
		# NOTE: Here PURPOSE (purpose) is using for Couse ID 
		pymtDetailsApiUrl = str(MOJO_PAYMENT_URL_HOST)+'/api/1.1/payments/'+str(payment_id)
		headers = { "X-Api-Key": MOJO_API_KEY, "X-Auth-Token": MOJO_AUTH_TOKEN}
		pymtDetailsResponse = requests.get(pymtDetailsApiUrl, headers=headers)
		jsonPymtDetailsResponse = json.loads(pymtDetailsResponse.text)
		pymtDetailsRespStatus = jsonPymtDetailsResponse['success']
		pymtSuccessStatus = jsonPymtDetailsResponse['payment']['status']
		# ends here ~ call instamojo api to get payment details

		# code works according to pymtDetailsResponse (payment gateway response) variable
		
		if(pymtDetailsRespStatus == True and pymtSuccessStatus != 'Failed'):
			# if payment is done successully
			pymtRespData = jsonPymtDetailsResponse['payment']
			
			####################################################
			# call API for Get Payment Request Details 
			pymtReqDetailsApiUrl = str(MOJO_PAYMENT_URL_HOST)+'/api/1.1/payment-requests/'+str(payment_request_id)+'/'
			pymtReqDetailsResp = requests.get(pymtReqDetailsApiUrl, headers=headers)
			jsonPymtReqDetailsResponse = json.loads(pymtReqDetailsResp.text)
			pymtReqRespData = jsonPymtReqDetailsResponse['payment_request']
			purpose = pymtReqRespData['purpose']
			eventTktAmtPaid = pymtReqRespData['amount']
			# ends here ~ call API for Get Payment Request Details
			########################################################

			purpose_list = purpose.split(',')

			eventId = int(purpose_list[0])
			tktQty = int(purpose_list[1])
			userId = int(purpose_list[2])

			buyer_email = pymtRespData['buyer_email']
			buyer_name = pymtRespData['buyer_name']
			amount = pymtRespData['amount']

			addTktPurch(eventId,userId,tktQty,payment_id,payment_request_id,eventTktAmtPaid,buyer_name,buyer_email)			
			# return thankYou Page on success of payment
			reverseUrl = reverse('attendee_site:thank-you',kwargs={'event_id':eventId,'payment_id':payment_id})
			return redirect(reverseUrl)
			# ends here ~ return thankYou Page on success of payment


		elif(pymtSuccessStatus == 'Failed'):
			# return thankYou Page on success of payment
			reverseUrl = reverse('attendee_site:payment-failed',kwargs={'event_id':0,'payment_id':0})
			return redirect(reverseUrl)
			# ends here ~ return thankYou Page on success of payment
		# ends here ~ code works according to pymtDetailsResponse (payment gateway response) variable

	except Exception as e:
		print('error in coursePaymentSuccess function >> ',e)
# ends here ~ function works when instamojo sends payment (success or failed) response from (instamojo) server after making payment

# def 
@csrf_exempt
def addTktPurch(event_id,purch_by_user_id,tkt_qty,payment_id,payment_request_id,amount_paid,buyer_name,buyer_email):
	purch_date = datetime.now()
	invoice_number = uuid.uuid4().hex[:10]
	TktPurchaseDetails.objects.create(event_id=event_id,purch_by_user_id=purch_by_user_id,purch_date=purch_date,tkt_qty=tkt_qty,payment_id=payment_id,payment_request_id=payment_request_id,invoice_number=invoice_number,amount_paid=amount_paid)

	# get event name
	evenetDetailObj = EventDetails.objects.get(id=event_id)
	eventName = evenetDetailObj.event_name
	venue = evenetDetailObj.venue
	totalTktSales = evenetDetailObj.total_tkt_sales
	totalTktSales = totalTktSales+tkt_qty
	EventDetails.objects.filter(id=event_id).update(total_tkt_sales=totalTktSales)
	# ends here ~ get event name

	# send invoice email
	contactEmail = settings.CONTACT_EMAIL
	websiteUrl = settings.WEBSITE_URL
	replyToEmail = settings.REPLY_TO_EMAIL
	
	subject = 'Invoice | Event Management'
	email_from = settings.EMAIL_WITH_DISPLAY_NAME
	recipient_list = [buyer_email]
	html_message = render_to_string('static/email_templates/event_ticket_invoice.html',{
			'website_url':websiteUrl,
			'contact_email':contactEmail,
			'buyer_name':buyer_name,
			'event_name': eventName,
			'invoice_number':invoice_number,
			'amount_paid':amount_paid,
			'tkt_qty':tkt_qty,
			'venue':venue
		})
	msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': replyToEmail})
	msg.content_subtype = "html"
	msgSentStatus = msg.send(fail_silently=False)
	# ends here ~ send invoice email
# ends here 

 # thank you page
def thankYou(request, event_id, payment_id):
	try:
		courseSalesFilter = TktPurchaseDetails.objects.get(payment_id=payment_id)
		purchaseDate = courseSalesFilter.purch_date
		amountPaid = courseSalesFilter.amount_paid
		return render(request, 'attendee_site/thank-you.html',{'paymentId':payment_id,'purchaseDate':purchaseDate,'amountPaid':amountPaid})
	except Exception as e:
		print('error in thank you page >> ', e)
		paymentId = 'N/A'
		purchaseDate = 'N/A'
		amountPaid = 'N/A'
		return render(request, 'attendee_site/thank-you.html',{'paymentId':paymentId,'purchaseDate':purchaseDate,'amountPaid':amountPaid})
# ends here ~ thank you page

# payment failed page
def paymentFailed(request, event_id, payment_id):
	return render(request, 'attendee_site/payment-failed.html')
# ends here ~ payment failed page

# function for cancel enrollment
@csrf_exempt
def cancelEnrollment(request, event_id):
	try:
		userId = isAttendeeUserLogin(request)
		if (userId == False):
			return HttpResponseRedirect(reverse('login'))

		# read request data
		requestData = request.body
		requestDataDecode = requestData.decode('utf8').replace("'", '"')
		requestDataJson = json.loads(requestDataDecode)
		# ends here ~ read request data

		# set request data into variable
		event_id = requestDataJson['event_id']
		# ends here ~ set request data into variable

		# filter and insert data into Cashback Records
		tktPurchObj = TktPurchaseDetails.objects.get(event_id=event_id)
		tkt_purch_id=tktPurchObj.id
		cashbackRecords.objects.create(tkt_purch_id=tkt_purch_id,event_id=event_id,user_id=userId,is_cashback_receive=False)
		# ends here ~ filter and insert data into Cashback Records

		# return data
		messageData = {'responseType':'success', 'messageType':'success', 'message':'Your request is sent for Ask for 50% Cashback by withdrawing from this Event', 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':True}
		return HttpResponse(json.dumps(messageData))
		# ends here ~ return data

	except Exception as e:
		pass

# ends here ~ function for cancel enrollment