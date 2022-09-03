from dataclasses import fields
from time import time
from rest_framework import serializers
from chat.models import Contacts, Messages , Reminders
from django.db.models import Q



class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        exclude = ["sent","sender_name","time","timestamp"]

class MessageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = "__all__"

class MessageViewSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()
    sent = serializers.SerializerMethodField()

    class Meta:
        model = Messages
        exclude = ["time"]
    
    def get_timestamp(self, obj):
        if obj.timestamp:
            return int(obj.timestamp.timestamp())
    
    def get_sent(self,obj):
        if obj.sender_name == self.context["request"].user.username:
            return True
        return False
    




class ContactViewSerializer(serializers.ModelSerializer):
    contact = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()
    last_message = MessageSerializer()
    absolute_url = serializers.SerializerMethodField()
    websocket_url = serializers.SerializerMethodField()
    unseen = serializers.SerializerMethodField()
    class Meta:
        model = Contacts
        fields = "__all__"
    def get_timestamp(self, obj):
        if obj.last_message:
            return int(obj.last_message.timestamp.timestamp())
        else:
            return 0
    
    def get_websocket_url(self,obj):
        return f"wss://srestatechat.herokuapp.com/ws/chat/{obj.owner}_{obj.contact}/"
    
    def get_contact(self,obj):
        if obj.owner == "BrokerBookAssitant":
            return obj.owner
        else:
            return obj.contact
    
    def get_absolute_url(self,obj):
        request = self.context["request"]
        return request.build_absolute_uri(f'/chats/contact_details/{request.user.mobile}/{obj.contact}/')

    def get_unseen(self,obj):
        return len(Messages.objects.filter(Q(sender_name=obj.owner, receiver_name = obj.contact , seen = 0)|
                Q(receiver_name=obj.owner, sender_name = obj.contact, seen=0 )))
class ContactDetailViewSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()
    
    class Meta:
        model = Contacts
        fields = "__all__"
    def get_timestamp(self, obj):
        if obj.last_message:
            return int(obj.last_message.timestamp.timestamp())
        return 0

class ContactReminderViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacts
        fields = ["contact"]


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminders
        exclude = ["contact"]

class ReminderViewSerializer(serializers.ModelSerializer):
    contact = ContactReminderViewSerializer()
    time = serializers.SerializerMethodField()
    class Meta:
        model = Reminders
        fields = "__all__"
    def get_time(self, obj):
        if obj.time:
            return int(obj.time.timestamp())
        return 0


        
    
