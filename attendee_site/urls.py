from django.contrib import admin
from django.urls import path, include
from . import views 

app_name = 'attendee_site'

urlpatterns = [
    path('',views.attendeeDashboard, name='attendee-dashboard'),
    path('event-list/<int:page_number>',views.eventList, name='event-list'),
    path('buy-ticket/<int:event_id>',views.buyTicket, name='buy-ticket'),
    path('event-payment-success',views.eventPaymentSuccess,name='event-payment-success'),
    path('thank-you/<int:event_id>/<str:payment_id>',views.thankYou,name='thank-you'),
    path('payment-failed/<int:event_id>/<str:payment_id>',views.paymentFailed,name='payment-failed'),
    path('cancel-enrollment/<int:event_id>',views.cancelEnrollment,name='cancel-enrollment')
]
