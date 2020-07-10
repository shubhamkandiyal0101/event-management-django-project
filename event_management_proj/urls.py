"""digital_saurav URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views 

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('',views.websiteHome, name='website-home'),
    path('signup',views.userSignup, name='signup'),
    path('login',views.userLogin, name='login'),
    path('logout',views.userLogout, name='logout'),
    path('contact',views.contactUs, name='contact'),
    path('about',views.aboutUs, name='about'),
    path('gen-dynamic-purpose-token',views.genDynamicPurposeToken, name='gen-dynamic-purpose-token'),
    path('event-detail/<int:event_id>',views.viewEventDetails, name='view-event-details'),
    path('reset-password/<str:token>',views.resetPassword,name='reset-password'),

    # include urls here
    path('organizer/',include('organizer_site.urls')),
    path('attendee/',include('attendee_site.urls')),
    # path('student-panel/',include('student_panel.urls'))
    # ends here ~ include urls here



    # path('login/<str:loginUsertype>',views.login, name='login'),
    # path('logout/',views.logout, name='logout'),
    # path('all-courses/',views.allCourses, name='all-courses'),
    # path('dynamic-user-login/<str:usertype>',views.dynamicUserLogin, name='dynamic-user-login'),
    # path('buy-course/<int:course_id>/<int:referrer_user_id>/<str:custom_url>/',views.buyCourse,name='buy-course'),
    # path('course-payment-success',views.coursePaymentSuccess,name='course-payment-success'),
    # path('thank-you/<int:courseId>/<int:referrerId>/<str:paymentId>/',views.thankYou,name='thank-you'),
    # path('payment-failed/<int:courseId>/<int:referrerId>/<str:paymentId>/',views.paymentFailed,name='payment-failed'),
    # path('gen-dynamic-purpose-token',views.genDynamicPurposeToken,name='gen-dynamic-purpose-token'),
    # path('reset-password/<str:token>',views.resetPassword,name='reset-password'),
    # path('sign-up',views.signUp, name='sign-up'),


]
# handler404 = 'digital_saurav.views.handler404'
# handler500 = 'digital_saurav.views.handler404'
