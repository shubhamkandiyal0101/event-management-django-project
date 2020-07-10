# import
from django.shortcuts import render, redirect, render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMessage, send_mail
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth.hashers import make_password, check_password
from django.template.loader import render_to_string
from django.urls import reverse
import hashlib
import uuid
import json
# from instamojo_wrapper import Instamojo
from django.conf import settings
# import requests
from datetime import datetime
import datetime as dt
import pytz
from django.utils import timezone
from django.template import RequestContext

# models
from django.contrib.auth.models import User
from .models import ManualTokenStorage, HimachalDistrict, EventDetails
# ends here ~ models

# ends here ~ import


# def handler404(request, *args, **argv):
# 	response = render_to_response('error_404.html')
# 	return response

######################

def websiteHome(request):
	return render(request, 'index.html')

@csrf_exempt
def userSignup(request):
	try:
		if request.method == 'GET':
			return render(request, 'signup.html')

		if request.method == 'POST':
			redirectUrl = reverse('login')
				
			# read request data
			requestData = request.body
			requestDataDecode = requestData.decode('utf8').replace("'", '"')
			requestDataJson = json.loads(requestDataDecode)
			# ends here ~ read request data

			# set request data into variable
			password = requestDataJson['password']
			email = requestDataJson['email']
			lastName = requestDataJson['last_name']
			firstName = requestDataJson['first_name']
			otp = requestDataJson['otp']
			is_staff = requestDataJson['is_staff']
			# ends here ~ set request data into variable

			userFilter = User.objects.filter(email=email)
			if(len(userFilter) > 0):
				messageData = {'responseType':'success', 'messageType':'error', 'message':'User Account is Already Exists with this email. Please try to login Your Account', 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False}
				return HttpResponse(json.dumps(messageData))


			# make password encrypted
			encrytpedPassword = make_password(password)
			# ends here ~ make password encrypted

			# verify token is valid or not
			manualTokenFilter = ManualTokenStorage.objects.filter(token=otp,token_purpose='activate_account',email=email)

			if(len(manualTokenFilter) == 1):
				ManualTokenStorage.objects.filter(token=otp,token_purpose='activate_account',email=email).delete()
				# create account
				userName = uuid.uuid4().hex[:10]
				User.objects.create(email=email, first_name=firstName, last_name=lastName, password=encrytpedPassword,username=userName, is_staff=is_staff, is_superuser=False, is_active=True)
				# ends here ~ create account

				redirectUrl = reverse('login')
				messageData = {'responseType':'success', 'messageType':'success', 'message':'Account Created Successfully. Page automatically Redirect to Login Page', 'responseData':[], 'nextPageUrl':str(redirectUrl), 'isRedirectNext':True}
			else:
				messageData = {'responseType':'success', 'messageType':'error', 'message':'Its seems like OTP is Invalid or Expired. Please request for new OTP', 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False}
			# ends here ~ verify token is valid or not

			
			return HttpResponse(json.dumps(messageData))
			# ends here ~ update User Table and return message

	except Exception as e:
		print(' Error in signup function >> ',e)


# function for organizer login ~ call from function (not directly)
def organizerLogin(request, emailPar):
	try:
		userFilterData = User.objects.get(email=emailPar,is_superuser=False,is_active=True,is_staff=True)
		
		# set values into session for admin user login
		request.session['user_id'] = userFilterData.id
		request.session['user_type'] = 'organizer'
		# ends here ~ set values into session for admin user login

		redirectUrl = reverse('organizer_site:organizer-dashboard')
		
		messageData = {'responseType':'success', 'messageType':'success', 'message':'Organizer User login Successfully', 'responseData':[], 'nextPageUrl':str(redirectUrl), 'isRedirectNext':True}
		return HttpResponse(json.dumps(messageData))
		
	except Exception as e:
		print('error in organizerLogin >> ',e)
		# code block works if password is invalid
		messageData = {'responseType':'success', 'messageType':'error', 'message':'Credentials is invalid for Admin User', 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False}
		return HttpResponse(json.dumps(messageData))
# ends here ~ function for admin login ~ call from function (not directly)

# function for admin login ~ call from function (not directly)
def attendeeLogin(request, emailPar):
	try:
		userFilterData = User.objects.get(email=emailPar,is_superuser=False,is_active=True,is_staff=False)
		
		# set values into session for admin user login
		request.session['user_id'] = userFilterData.id
		request.session['user_type'] = 'attendee'
		# ends here ~ set values into session for admin user login

		redirectUrl = reverse('attendee_site:attendee-dashboard')
		
		messageData = {'responseType':'success', 'messageType':'success', 'message':'Attendee User login Successfully', 'responseData':[], 'nextPageUrl':str(redirectUrl), 'isRedirectNext':True}
		return HttpResponse(json.dumps(messageData))
		
	except Exception as e:
		print('error in attendeeLogin >> ',e)
		# code block works if password is invalid
		messageData = {'responseType':'success', 'messageType':'error', 'message':'Credentials is Invalid for Attendee User', 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False}
		return HttpResponse(json.dumps(messageData))
# ends here ~ function for admin login ~ call from function (not directly)

@csrf_exempt
def userLogin(request):
	try:
		# GET method
		if request.method == 'GET':
			return render(request, 'login.html')
		# ends here ~ GET method

		# POST method
		if request.method == 'POST':
			# read request data
			requestData = request.body
			requestDataDecode = requestData.decode('utf8').replace("'", '"')
			requestDataJson = json.loads(requestDataDecode)
			# ends here ~ read request data

			# set request data into variables
			email = requestDataJson['email']
			user_type = requestDataJson['user_type']
			password = requestDataJson['password']
			# ends here ~ set request data into variable

			try:
				userFilterData = User.objects.get(email=email)
				userPasswordConfirmation = check_password(password,userFilterData.password)

				if (userPasswordConfirmation == True):
					
					# check user type and login user according to that url
					if user_type == 'organizer':
						return organizerLogin(request, email)
					elif user_type == 'attendee':
						return attendeeLogin(request, email)
					# ends here ~ check user type and login user according to that url 

				else:
					# code block works if password is invalid
					messageData = {'responseType':'success', 'messageType':'error', 'message':'Invalid Password for '+ str(email), 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False}
					return HttpResponse(json.dumps(messageData))

			except Exception as e:
				messageData = {'responseType':'success', 'messageType':'error', 'message':str(email) +' is not Exists in Our Database', 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False}
				return HttpResponse(json.dumps(messageData))
		# ends here ~ POST method

	except Exception as e:
		print(' error in userLogin function >> ',e)

def contactUs(request):
	return render(request, 'contact.html')

def aboutUs(request):
	return render(request, 'about.html')


##################################################################


# function for send forgot password email
def sendForgotPasswordEmail(hostUrl, userEmailId, userFullname, token):
	try:
		contactEmail = settings.CONTACT_EMAIL
		websiteUrl = settings.WEBSITE_URL
		replyToEmail = settings.REPLY_TO_EMAIL
		
		forgotPswdUrl = str(hostUrl)+'/reset-password/'+str(token)

		subject = 'Reset Password | Event Management'
		email_from = settings.EMAIL_WITH_DISPLAY_NAME
		recipient_list = [userEmailId]
		html_message = render_to_string('static/email_templates/forgot_password.html',{
				'website_url':websiteUrl,
				'contact_email':contactEmail,
				'full_name':userFullname,
				'forgot_pswd_url': forgotPswdUrl
			})
		msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': replyToEmail})
		msg.content_subtype = "html"
		msgSentStatus = msg.send(fail_silently=False)

		# code block works on successfully send email 
		if msgSentStatus == 1:
			return {'message':{'responseType':'success', 'messageType':'success', 'message':'Reset Password Email is Sent Successfully. Please Check Your Email Inbox/SPAM Box. Its might be take 5-15 Minutes to Recieve Email', 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False},'sent_status':msgSentStatus}
		else:
			return {'message':{'responseType':'success', 'messageType':'error', 'message':'Forgot Password Email not Sent Successfully. Please try Again', 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False},'sent_status':msgSentStatus}
		# ends here ~ code block works on successfully send email
	except Exception as e:
		return {'message':{'responseType':'success', 'messageType':'error', 'message':'Forgot Password Email not Sent Successfully. Please try Again', 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False},'sent_status':msgSentStatus}

# ends here ~ function for send forgot password email

# function for send Email OTP
def sendAccActivateEmailOTP(userEmailId, token):
	try:
		userFilter = User.objects.filter(email=userEmailId)
		if(len(userFilter) > 0):
			return {'message':{'responseType':'success', 'messageType':'error', 'message':'E-Mail is Already Exists in Our Records. Please use another Email', 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False},'sent_status':0}

		contactEmail = settings.CONTACT_EMAIL
		websiteUrl = settings.WEBSITE_URL
		replyToEmail = settings.REPLY_TO_EMAIL
		
		subject = 'OTP | Event Management'
		email_from = settings.EMAIL_WITH_DISPLAY_NAME
		recipient_list = [userEmailId]
		html_message = render_to_string('static/email_templates/account_activate_otp.html',{
				'website_url':websiteUrl,
				'contact_email':contactEmail,
				'otp': token
			})
		msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': replyToEmail})
		msg.content_subtype = "html"
		msgSentStatus = msg.send(fail_silently=False)

		# code block works on successfully send email 
		if msgSentStatus == 1:
			return {'message':{'responseType':'success', 'messageType':'success', 'message':'OTP Sent to E-Mail Successfully. Please Check Your Email Inbox/SPAM Box. Its might be take 2-3 Minutes to Recieve Email', 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False},'sent_status':msgSentStatus}
		else:
			return {'message':{'responseType':'success', 'messageType':'error', 'message':'OTP Email not Sent Successfully. Please try Again', 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False},'sent_status':msgSentStatus}
		# ends here ~ code block works on successfully send email
	except Exception as e:
		return {'message':{'responseType':'success', 'messageType':'error', 'message':'OTP Email not Sent Successfully. Please try Again', 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False},'sent_status':0}
# ends here ~ function for send Email OTP

# generate dynamic purpose token 
@csrf_exempt
def genDynamicPurposeToken(request):
	try:
		if request.method == 'POST':
			# read request data
			requestData = request.body
			requestDataDecode = requestData.decode('utf8').replace("'", '"')
			requestDataJson = json.loads(requestDataDecode)
			# ends here ~ read request data

			# set settings file variables
			contactEmail = settings.CONTACT_EMAIL
			websiteUrl = settings.WEBSITE_URL
			replyToEmail = settings.REPLY_TO_EMAIL
			# ends here ~ set settings file variables

			# set request data into variables
			email = requestDataJson['email']
			token_purpose = requestDataJson['token_purpose']
			# ends here ~ set request data into variables

			# get 3 day valid till date
			today = dt.date.today()
			token_expire_datetime = today + dt.timedelta(3)
			utc = pytz.UTC
			# ends here ~ get 3 day valid till date

			# generate token
			token = uuid.uuid4().hex[:10]
			# ends here ~ generate token

			hostUrl = request.META['HTTP_ORIGIN']

			if token_purpose == 'activate_account':
				setTimeDiff = 3
			else:
				# check email is exists in User table or not
				try:
					userFilter = User.objects.get(email=email)
				except Exception as e:
					messageData = {'responseType':'success', 'messageType':'error', 'message':'Email is not Exists in Our Records', 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False}
					return HttpResponse(json.dumps(messageData))
				# ends here ~ check email is exists in User table or not

				# set required data into variable
				userEmailId = userFilter.email
				userFirstname = userFilter.first_name
				userLastname = userFilter.last_name
				userFullname = userFirstname + ' ' + userLastname
				setTimeDiff = 15
				# ends here ~ set required data into variable


			# filter data from ManualTokenStorage table 
			tokenStorageFilter = ManualTokenStorage.objects.filter(token_purpose=token_purpose,email=email).values()
			# ends here ~ filter data from ManualTokenStorage table

			if len(tokenStorageFilter) == 0:

				# send email
				if token_purpose == 'forgot-password':
					MsgDataFromFn = sendForgotPasswordEmail(hostUrl, userEmailId, userFullname, token)
				elif token_purpose == 'activate_account':
					MsgDataFromFn = sendAccActivateEmailOTP(email, token)
				# ends here ~ send email

				# generate token
				if MsgDataFromFn['sent_status'] == 1:
					ManualTokenStorage.objects.create(token=token,generate_date=datetime.now(),token_expire_dt=token_expire_datetime,token_purpose=token_purpose,email=email)
				# ends here ~ generate token


				# message for response
				messageData = MsgDataFromFn['message']
				# ends here ~ message for response
			else:
				tokenStorageObjectDict = tokenStorageFilter[0]
				tokenGenerateDate = tokenStorageObjectDict['generate_date']
				
				currentUtcDt = utc.localize(datetime.utcnow())
				timediff = currentUtcDt - tokenGenerateDate
				timeDiffMin = timediff.seconds/60

				if(timeDiffMin > setTimeDiff):

					# send email
					if token_purpose == 'forgot-password':
						MsgDataFromFn = sendForgotPasswordEmail(hostUrl, userEmailId, userFullname, token)
					elif token_purpose == 'activate_account':
						MsgDataFromFn = sendAccActivateEmailOTP(email, token)
					# ends here ~ send email

					# update token to db
					if MsgDataFromFn['sent_status'] == 1:
						ManualTokenStorage.objects.filter(token_purpose=token_purpose,email=email).update(token=token,generate_date=datetime.now(),token_expire_dt=token_expire_datetime)
					# ends here ~ update token to db

					# message for response
					messageData = MsgDataFromFn['message']
					# ends here ~ message for response
				else:
					remainingTokenGen = (setTimeDiff*60)-timediff.seconds
					returnAjaxMessage = 'Its seems like Email is Already Sent. If You did not recieved any Email Yet. Then Please check Email Again. ' + str(int(remainingTokenGen/60)) + ' Minutes ' + str(int(remainingTokenGen%60)) + ' Seconds'
					# message for response
					messageData = {'responseType':'success', 'messageType':'info', 'message': str(returnAjaxMessage), 'responseData':[], 'nextPageUrl':'', 'isRedirectNext':False}
					# ends here ~ message for response

			return HttpResponse(json.dumps(messageData))

	except Exception as e:
		print(' error in genDynamicPurposeToken function >> ',e)
# ends here ~ generate dynamic purpose token

# function for get all district
def getAllDistrict():
	himachalDistrictList = list(HimachalDistrict.objects.all().values('id','district_val','district_name'))
	return himachalDistrictList
# ends here ~ function for get all district

# function for view event details
def viewEventDetails(request, event_id):
	try:
		field_list = ['event_name','event_short_desc','event_long_desc','image','venue','pincode','venue_district__district_name','event_start_datetime','event_end_datetime','tkt_start_datetime','tkt_end_datetime','total_tkt_qty','tkt_price','total_tkt_sales','date_added','date_modified','user_id']
		# get event details according to id
		eventDetailsFilter = EventDetails.objects.filter(id=event_id).values(*field_list)
		# ends here ~ get event details according to id

		if(len(eventDetailsFilter) == 0):
			HttpResponseRedirect(reverse(''))

		# GET Method
		if request.method == 'GET':
			himachalDistrictList = getAllDistrict()
			eventDetailsDict = list(eventDetailsFilter)[0]
			return render(request, 'event_details.html',{'event_detail':eventDetailsDict})
		# ends here ~  GET method

	except Exception as e:
		print(' >> error in viewEventDetails function >> ',e)

# function for logout user
def userLogout(request):
	sessionKeys = list(request.session.keys())
	for key in sessionKeys:
		del request.session[key]
	return HttpResponseRedirect(reverse('login'))

# ends here ~ function for logout user


# function for reset password
@csrf_exempt
def resetPassword(request, token):
	try:
		# GET request
		if request.method == 'GET':
			try:
				manualTokenFilter = ManualTokenStorage.objects.get(token=token)
				return render(request, 'reset-password.html')
			except Exception as e:
				return render(request, 'reset-password.html', {'showError':1,'errorMessage':'Its seems like You are using Expired or Invalid Link to Reset Password'})
		# ends here ~ GET request

		# POST request
		if request.method == 'POST':
			redirectUrl = reverse('login')
			try:
				# read request data
				requestData = request.body
				requestDataDecode = requestData.decode('utf8').replace("'", '"')
				requestDataJson = json.loads(requestDataDecode)
				# ends here ~ read request data

				# set password into variable & make encrypted
				password = requestDataJson['password']
				encrytpedPassword = make_password(password)
				# ends here ~ set password into variable & make encrypted

				# filter ManualTokenStorage table and get email 
				manualTokenFilter =  ManualTokenStorage.objects.get(token=token)
				email = manualTokenFilter.email
				# ends here ~ filter ManualTokenStorage table and get email

				# update User Table and return message 

				User.objects.filter(email=email).update(password=encrytpedPassword)
				messageData = {'responseType':'success', 'messageType':'success', 'message':'Password is Successfully Updated. Please login with New Password', 'responseData':[], 'nextPageUrl':str(redirectUrl), 'isRedirectNext':True}

				# delete token from table
				ManualTokenStorage.objects.filter(token=token).delete()
				# ends here ~ delete token from table

				return HttpResponse(json.dumps(messageData))
				# ends here ~ update User Table and return message

			except Exception as e:
				print(' error in resetPassword function | POST Request >> ',e)

				messageData = {'responseType':'success', 'messageType':'error', 'message':'Its seems like You are using Expired or Invalid Link to Reset Password', 'responseData':[], 'nextPageUrl':str(redirectUrl), 'isRedirectNext':True}
				return HttpResponse(json.dumps(messageData))
		# ends here ~ POST request
	except Exception as e:
		print(' error in resetPassword main function >> ',e)
# ends here ~ function for reset password