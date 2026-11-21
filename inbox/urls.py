from django.urls import path

from inbox import views

urlpatterns = [
    path("whatsapp/inbound/", views.whatsapp_inbound, name="whatsapp_inbound"),
]