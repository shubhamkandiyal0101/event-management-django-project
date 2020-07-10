from django.contrib import admin
from django.urls import path, include
from . import views 

app_name = 'organizer_site'

urlpatterns = [
    path('',views.organizerDashboard, name='organizer-dashboard'),
    path('add-event',views.addEvent, name='add-event'),
    path('list-event',views.listEvent, name='list-event'),
    path('edit-event/<int:event_id>',views.editEvent, name='edit-event'),
    path('update-event-img/<int:event_id>',views.updateEventImg, name='update-event-img'),
    path('delete-event',views.deleteEvent, name='delete-event'),
    path('ticket-cancel-req',views.ticketCancelReq, name='ticket-cancel-req'),
]
