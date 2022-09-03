from django.urls import path
from django.conf.urls import  url
from chat import  views

urlpatterns = [
    path("create/", views.CreateMessageAPIView.as_view(),name="Messages_create"),
    path("contactlist/", views.ListContactAPIView.as_view(), name="contact_list"),
    path("reminderlist/", views.ListReminderAPIView.as_view(), name="reminder_list"),
    path("chatbymobile/",views.chatByMobile , name="chat_by_mobile"),
    path("reply/", views.demo_reply, name="chat_reply"),
    path("create/reminder/", views.create_reminder,name="reminder"),
    path("contact_details/<str:broker>/<str:client>/", views.get_contact_detail_view , name="contacts_details"),
    path("seen_update/", views.chat_room_seen_update,name="seen_update")
]