from celery import task 
from celery import shared_task 
# We can have either registered task 
from chat.models import Messages,Contacts
from srestate.celery import app as celery_app
from UserManagement.utils import send_whatsapp_msg 
import asyncio
import websockets
import json
from property.location.location_views import db
from srestate.config import CACHES
import redis
from collections import defaultdict

cache = redis.Redis(
host=CACHES["default"]["host"],
port=CACHES["default"]["port"], 
password=CACHES["default"]["password"])



def merge_dict(list_of_dict):
    dd = defaultdict(list)
    
    for d in list_of_dict: # you can list as many input dicts as you want here
        for key, value in d.items():
            if isinstance(value, list):
                dd[key] = list(set(dd[key]+value))
            elif value not in dd[key]:
                dd[key].append(value)

    return dict(dd)

# or 
@celery_app.task(bind=True, time_limit=2700)
def send_notifiction(self,data):
    print("summary")
    print(data)
    send_whatsapp_msg(data["reciever_name"],data["description"])
    send_whatsapp_msg(data["sender_name"],data["description"])

@celery_app.task(bind=True, time_limit=2700)
def seen_update(self,data,sender_name,reciver_name):
    contact = Contacts.objects.get(owner = sender_name, contact = reciver_name)
    print(data)
    loop = asyncio.new_event_loop()
    for message in data:
        if "id" not in message.keys():
            print("no id found")
            return
        chat_message = Messages.objects.get(pk=message["id"])
        chat_message.seen = True
        chat_message.save()
    #     try:
    #         timeout = 5
    #         asyncio.set_event_loop(loop)
    #         websocket_url = f"wss://srestatechat.herokuapp.com/ws/chat/{contact.owner}_{contact.contact}/"         
    #         ws_conn = loop.run_until_complete(websockets.connect(websocket_url))               
    #         loop.run_until_complete(ws_conn.send(json.dumps({"message":f"{chat_message.id}","sender":sender_name,"sent":False,"message_type":"seen_update" })))
    #         return True
    #     except Exception as e:
    #         print("websocket Error " ,e)

    # loop.run_until_complete(ws_conn.close())

@celery_app.task(bind=True, time_limit=2700)
def create_contact_message(self,data,send,recieve,interested):
    try:
        if "estates" in data.keys() and list(data["estates"]):
            contact_found,created = Contacts.objects.get_or_create(
                owner = send,
                contact = recieve
            )
            print(data["estates"],type(data["estates"]))
            if created:
                eststate_list = ""
                print(eststate_list)
                for x in data["estates"]:
                    eststate_list = str(x) +"," + eststate_list
                print(eststate_list)
                contact_found.eststate_list = eststate_list
                contact_found.save()
                print(contact_found)
            else:
                old_list =[]
                eststate_list = contact_found.eststate_list
                print(eststate_list)
                old_list = contact_found.eststate_list.split(",")
                for x in data["estates"]:
                    if str(x) != "" and str(x) not in old_list :
                        print(x)
                        eststate_list = f"{str(x)}," + eststate_list
                print(eststate_list)
                print("here2")
                contact_found.eststate_list = eststate_list
                contact_found.save()
            print("here1")
    except Exception as e:
        print(str(e))  
        
@celery_app.task(bind=True, time_limit=2700)
def create_or_update_customer_query(self,data,mobile_number,owner,findQuery,interested):
    try:
        if not interested:
            contact = False
            mycol = db.property_estate
            queryset= mycol.find(findQuery,{ '_id': False})
            listestate =[]
            if queryset:
                listestate = list(queryset)
                contact = db.property_enquiryquerys.find_one({"broker_number":owner,"mobile_number":mobile_number})
                if not contact:
                    contact = {"broker_number":owner,"mobile_number":mobile_number}
                listestate.append(contact.get("query",{}))
                contact["query"] = merge_dict(listestate)
                contact = db.property_enquiryquerys.update({"broker_number":owner,"mobile_number":mobile_number},{"query":contact["query"]},upsert=True)
    except Exception as e:
        print(str(e))