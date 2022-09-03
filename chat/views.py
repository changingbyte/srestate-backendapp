from email import message
from django.forms.models import model_to_dict
import asyncio
from chat import serializers
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, UpdateAPIView)
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from property.location.location_views import db
from django.http import JsonResponse
from property.estate.wputils import get_data_from_msg
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.decorators import renderer_classes, api_view 
from UserManagement.utils import send_sms ,send_whatsapp_msg   ,find_related_db
from chat.models import Messages,Contacts, Reminders
from chat.serializers import ContactDetailViewSerializer, MessageSerializer ,MessageViewSerializer , ContactViewSerializer , ReminderSerializer , ReminderViewSerializer , MessageUpdateSerializer
from property.utils import ReturnResponse ,create_msg , ReturnJsonResponse
from datetime import datetime ,timedelta
from django.db.models import Q
import json
import websockets
from srestate.config import CACHES
import redis
from property.location.location_views import db
from chat.tasks import send_notifiction , seen_update
from property.estate.estate_serializers import EstateSerializer




cache = redis.Redis(
    host=CACHES["default"]["host"],
    port=CACHES["default"]["port"], 
    password=CACHES["default"]["password"])


# Create your views here.
# Create your views here.
def send_ws(WS_String,From,message):
    try:
        timeout = 5
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)              
        ws_conn = loop.run_until_complete(websockets.connect(WS_String))               
        loop.run_until_complete(ws_conn.send(json.dumps({"message":message,"sender":From,"sent":False,"message_type":"message" })))
        loop.run_until_complete(ws_conn.close())
        return True
    except Exception as e:
        print("websocket Error " ,e)

def create_msg_in_db(data,sender,recieved = False):
    serilizer = MessageSerializer(data=data)
    if serilizer.is_valid():
        if recieved:
            contact_send,created = Contacts.objects.get_or_create(
                contact = sender,
                owner = serilizer.validated_data["receiver_name"]
            )
            serilizer.validated_data["sender_name"] = sender
            serilizer.validated_data["sent"] = False
            message = serilizer.create(serilizer.validated_data)
        else:
            contact_send, created = Contacts.objects.get_or_create(
                owner = sender,
                contact  = serilizer.validated_data["receiver_name"]
            )
            serilizer.validated_data["sender_name"] = sender
            serilizer.validated_data["sent"] = True
            message = serilizer.create(serilizer.validated_data)

        contact_send.last_message = message
        contact_send.timestamp = datetime.now()
        contact_send.save()
        return message,True
    else:
        return serilizer.errors,False


class ListMessageAPIView(ListAPIView):
    queryset = Messages.objects.all()
    serializer_class = MessageViewSerializer


class CreateMessageAPIView(CreateAPIView):
    queryset = Messages.objects.all()
    serializer_class = MessageSerializer

    def post(self,request):
        if request.data["receiver_name"] != request.user.mobile:
            send_whatsapp_msg(request.data["receiver_name"],request.data["description"])
            message, sucess = create_msg_in_db(request.data,request.user.mobile)
        else:
            return ReturnResponse(success=True, status=status.HTTP_200_OK)
        if sucess:
            return ReturnResponse(success=True, status=status.HTTP_200_OK)
        else:
            return ReturnResponse(success=False,errors= message, status=status.HTTP_400_BAD_REQUEST)


@api_view(('POST',))
@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def create_reminder(request):
    contact,created = Contacts.objects.get_or_create(
        owner = request.data["sender_name"],
        contact = request.data["reciver_name"],
    )
    request.data.pop("reciver_name")
    request.data.pop("sender_name")
    

    print(request.data)
    serializer = ReminderSerializer(data=request.data)
    if serializer.is_valid():
        reminder = Reminders.objects.create(**serializer.data)
        reminder.contact = contact
        reminder.save()
        print("heelo", serializer.data)
        data = {
            "sender_name" : request.user.mobile,
            "reciever_name": contact.contact,
            "description":request.data["description"]
        }
        send_notifiction.apply_async(eta=(datetime.strptime(reminder.time,"%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=5, minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ"), args=[data])
        return ReturnJsonResponse(data =serializer.data ,success=True,msg="fetch successfully", status=status.HTTP_200_OK)
    else:
        return ReturnJsonResponse(data =serializer.errors ,success=False,msg="please fill all the fields", status=status.HTTP_400_BAD_REQUEST)





class ListContactAPIView(ListAPIView):
    serializer_class = ContactViewSerializer
    def get_queryset(self) :
        request = self.request
        queryset = Contacts.objects.filter(owner= request.user.mobile)
        return queryset


class ListReminderAPIView(ListAPIView):
    serializer_class = ReminderViewSerializer
    def get_queryset(self) :
        request = self.request
        queryset = Reminders.objects.filter(contact__owner= request.user.mobile)
        return queryset
        

@api_view(('GET',))
@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def get_contact_detail_view(request,broker,client) :
    queryset = Contacts.objects.filter(owner= broker ,contact = client).first()
    print(queryset)
    serializer = ContactViewSerializer( queryset , context={'request': request})
    data = serializer.data

    if f"{broker}_{client}" in cache:
        my_list = cache.get(f"{broker}_{client}")
        my_list = json.loads(my_list)
    else:
        mycol = db.property_estate
        findQuery ={}
        estate_list = serializer.data["eststate_list"].split(",")
        find_list = [int(x) for x in estate_list if x!= ""]
        findQuery["id"] = {"$in":find_list}
        my_list = list(mycol.find(findQuery))
        serializer = EstateSerializer(my_list,many = True, context={'request': request})
        my_list = serializer.data
    data["eststate_list"] =  my_list
    print(data["eststate_list"])
    return ReturnJsonResponse(data =data ,success=True,msg="fetch successfully", status=status.HTTP_200_OK)


@api_view(('GET',))
@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def chatByMobile(request):
    try:
        paginator = PageNumberPagination()
        paginator.page_size = 10
        mobile = request.GET.get('mobile')
        print(request.user)
        if mobile is None:
            return ReturnJsonResponse(errors=["please enter mobile"],success=False,msg="Invalid Request", status=status.HTTP_400_BAD_REQUEST)
        chats = Messages.objects.filter(
                Q(sender_name=request.user.mobile, receiver_name = mobile )|
                    Q(receiver_name=request.user.mobile, sender_name = mobile )
            )
        result_page = paginator.paginate_queryset(chats, request)
        if chats:
            serializer = MessageViewSerializer(chats,many = True , context={'request': request})
            return ReturnJsonResponse(data =serializer.data ,success=True,msg="fetch successfully", status=status.HTTP_200_OK)
        else:
            return ReturnJsonResponse(data = [],success=True,msg="PLease Send First Message", status=status.HTTP_200_OK)
    except Exception as e:
        print(str(e))
        return ReturnJsonResponse(errors=str(e),success=False,msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def demo_reply(request):
    From = request.POST["From"][12:]
    print(From)
    msg  = None
    multi = False
    if request.POST["Body"] is not None or str(request.POST["Body"]):

        
        mycol = db.UserManagement_user
        broker = mycol.find_one({"mobile":From})
        print(broker)
        if not broker:
            sender_list = Contacts.objects.filter(contact = From).last()
            if sender_list:
                sender = sender_list.owner
            
            data = {
                    "description":request.POST["Body"],
                    "receiver_name":sender,
                    "seen":False
                }
            WS_String  = f"wss://srestatechat.herokuapp.com/ws/chat/{sender}_{From}/"
            print(WS_String)# Once the task is created, it will begin running in parallel
            send_ws(WS_String,From,request.POST["Body"])
            
            message, sucess = create_msg_in_db(data,From,recieved=True)
        
            messageString = reply_related_estates(request.POST["Body"],From,sender)
        else:
            print("Broker_found")
            if request.POST["Body"][:5].lower() == "query":
                messageString = reply_related_estates(request.POST["Body"],From,From)
            elif request.POST["Body"][:3].lower() == "add":
                multi = True
                out_json = get_data_from_msg(request.POST["Body"],From,multi)
                if out_json:
                    messageString = create_msg(out_json)
                    print(messageString)
                    start_message = "*All below estate has been Created* \n \n"
                    send_whatsapp_msg(From,start_message + messageString[0])
                    
                else:
                    messageString = "Above message is not able for please add using \n *Broker Book App --> Create Estate Page*"
                    send_whatsapp_msg(From,messageString)
            else:
                messageString = "Please start Your message with either *query* \n or *add estate*"
                send_whatsapp_msg(From,messageString)

            


        return JsonResponse({"data": messageString},status = status.HTTP_200_OK)

def reply_related_estates(enquiry_message,From,sender):
    suggestion_message = ""
    if From == sender:
        suggestion_message ="Wow you have matching property too \n"
    out_json = get_data_from_msg(enquiry_message,From)
    if out_json:
        findQuery = out_json
        findQuery["broker_mobile"] = sender
        findQuery["id"] =0
        if "bhk" in enquiry_message and "estate_type" in findQuery:
            findQuery["estate_type"] = ['flat']
        mycol = db.property_estate
        queryset = find_related_db(mycol,findQuery)
        print(len(queryset))
        if queryset:
            messageString = create_msg(queryset)
            print(messageString)
            send_whatsapp_msg(From,suggestion_message +messageString[0])
            if suggestion_message == "":
                data = {
                    "description":messageString[0],
                    "receiver_name":From,
                    "seen":False
                }
                message, sucess = create_msg_in_db(data,sender)
        else:
            messageString = "no estate found"
            send_whatsapp_msg(From,messageString)
            if suggestion_message == "":
                data = {
                    "description":messageString[0],
                    "receiver_name":From,
                    "seen":False
                }
                message, sucess = create_msg_in_db(data,sender)
    else:
        messageString = "no query found"
        send_whatsapp_msg(From,messageString)
        if suggestion_message == "":
            data = {
                "description":messageString[0],
                "receiver_name":From,
                "seen":False
            }
            message, sucess = create_msg_in_db(data,sender)
    return messageString

@api_view(('POST',))
@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def chat_room_seen_update(request):
    try:
        print(request.data,"here")
        sender_number= request.user.mobile
        reciever_number = request.data["reciver_name"]
        print(sender_number,reciever_number)
        if request.data["reciver_name"] is not None:
            chats = Messages.objects.filter(Q(sender_name=sender_number, receiver_name = reciever_number , seen = False)|
                    Q(receiver_name=sender_number, sender_name = reciever_number, seen=False ))
            print("here")
            print(type(chats))
            
            
            serializer = MessageUpdateSerializer(chats,many = True)
            print(serializer.data)
            seen_update.apply_async(args=[serializer.data,sender_number,reciever_number])
            return JsonResponse({"data": "updated successfully"},status = status.HTTP_200_OK)
            
        else:
            return JsonResponse({"data": "Bad Request"},status = status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(str(e))
        return ReturnJsonResponse(errors=str(e),success=False,msg="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

