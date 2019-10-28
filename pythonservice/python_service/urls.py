"""python_service URL Configuration

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
from django.conf.urls import url
from pythonservice.python_service import uarm_service
from pythonservice.python_service import usbhub3p_service

urlpatterns = [
    url(r'^uArm/set_position$', uarm_service.set_position),
    url(r'^uArm/stop$', uarm_service.stop),
    url(r'^uArm/slide$', uarm_service.slide),
    url(r'^uArm/click$', uarm_service.click),
    url(r'^uArm/get_position$', uarm_service.get_position),
    url(r'^uArm/servo_detach$', uarm_service.servo_detach),
    url(r'^uArm/servo_attach$', uarm_service.servo_attach),
    url(r'^record/record_status$', uarm_service.execute_record_action),
    url(r'^sleep/sleep_time$', uarm_service.execute_sleep_action),

    url(r'^usbHub/openPort$', usbhub3p_service.setPortEnable),
    url(r'^usbHub/closePort$', usbhub3p_service.setPortDisable),
    url(r'^usbHub/openAllPort$', usbhub3p_service.setPortAllEnable),
    url(r'^usbHub/closeAllPort$', usbhub3p_service.setPortAllDisable),
]
