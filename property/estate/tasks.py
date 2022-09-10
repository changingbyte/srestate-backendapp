from ast import Delete
from celery import task 
from celery import shared_task 
from srestate.celery import app as celery_app
from property.models import EstateStatus, EstateType ,City,Apartment,Area , Broker
from property.location.location_views import db
from srestate.config import CACHES
import redis
import json
from property.estate.estate_serializers import EstateSerializer
from chat.models import Contacts
from property.utils import create_msg 
from property.models import Estate
import time
from chat.views import create_msg_in_db
from UserManagement.utils import send_sms ,send_whatsapp_msg 

cache = redis.Redis(
    host=CACHES["default"]["host"],
    port=CACHES["default"]["port"], 
    password=CACHES["default"]["password"])

def get_estate_name(obj):
    if obj['floor_space'] and obj['number_of_bedrooms']:
        obj['estate_name'] = f"{obj['estate_type']} {obj['estate_status']} {obj['number_of_bedrooms']}bhk {obj['floor_space']}sqft {obj['area']} {obj['society']}"
        return f"{obj['estate_type']} {obj['estate_status']} {obj['number_of_bedrooms']}bhk {obj['area']} {obj['society']}  {obj['floor_space']}sqft "
    elif obj['floor_space']:
        obj['estate_name'] =  f"{obj['estate_type']} {obj['estate_status']} {obj['floor_space']}sqft {obj['area']} {obj['society']}"
        return f"{obj['estate_type']} {obj['estate_status']} {obj['floor_space']}sqft {obj['area']} {obj['society']}"
    elif obj['number_of_bedrooms']:
        obj['estate_name'] =  f"{obj['estate_type']} {obj['estate_status']} {obj['number_of_bedrooms']}bhk {obj['area']} {obj['society']}"
        return f"{obj['estate_type']} {obj['estate_status']} {obj['number_of_bedrooms']}bhk {obj['area']} {obj['society']}"
    else:
        obj['estate_name'] =  f"{obj['estate_type']} {obj['estate_status']}  {obj['area']} {obj['society']}"
        return f"{obj['estate_type']} {obj['estate_status']}  {obj['area']} {obj['society']}"


@celery_app.task(bind=True, time_limit=2700)
def create_bulk_estate(self,data):
    start_time = time.time()
    print(f"start time {time.time()}")
    for data1 in data:
        estate = Estate.objects.create(**data1)

@celery_app.task(bind=True, time_limit=2700)
def create_estate_attribute(self,data1,mobile,balance):
    start_time = time.time()
    print(f"start time {time.time()}")
    for i in data1.keys():
        print(i,data1[i],type(data1[i]))
        if str(data1[i]).isdigit():
            data1[i] = int(data1[i])
        elif type(data1[i]) == str:
            data1[i] = data1[i].lower()
    print(f"end time {time.time()-start_time}")
    data1["broker_mobile"] = mobile
    estate = Estate.objects.create(
        estate_name = get_estate_name(data1),
        city = data1["city"],
        estate_type = data1["estate_type"],
        floor_space = data1["floor_space"],
        number_of_bedrooms = data1["number_of_bedrooms"],
        estate_description = data1["estate_description"],
        estate_status = data1["estate_status"],
        rent_status = data1["rent_status"] if data1["estate_status"] == "rent" else "",
        society = data1["society"] ,
        area = data1["area"],
        budget = data1["budget"],
        furniture  = data1["furniture"],
        broker_mobile = data1["broker_mobile"]
    )
    

    print(f"end time 1{time.time()-start_time}")
    print(f"start time 1 {time.time()-start_time}")

    if len(str(mobile)) == 10:
        broker,created = Broker.objects.get_or_create(
        mobile = int(mobile)
        )
        
    if data1["city"] is not None:
        city,created = City.objects.get_or_create(
        city_name = data1["city"].lower()
    )

    if data1["estate_type"] is not None:
        estate_type,created = EstateType.objects.get_or_create(
        type_name = data1["estate_type"].lower()
    )

    if data1["estate_status"] is not None:
        estate_status,created = EstateStatus.objects.get_or_create(
        estate_status_name = data1["estate_status"].lower()
    )

    if data1["area"] is not None:
        area,created = Area.objects.get_or_create(
        area_name = data1["area"].lower()
    )

    if data1["society"] is not None:
        society,created = Apartment.objects.get_or_create(
        apartment_name = data1["society"].lower(),
        area = data1["area"].lower()
    )
    mycol = db.UserManagement_user
    updatestmt = (
        {"mobile":mobile},
        {"$set":{
            "balance": balance + 100,
            "is_premium": True,
        }}
    )
    broker = mycol.update_one(*updatestmt)

@celery_app.task(bind=True, time_limit=2700)
def create_estate_cache(self,data1):
    try:
        cache.delete("filter_details")
        cache.delete(str(data1["broker_mobile"]) + "buy")
        cache.delete(str(data1["broker_mobile"]) + "sell")
        cache.delete("premium_buy")
        cache.delete("premium_sell")
        # cache.delete(str(data1["broker_mobile"]))
        cache.delete("required_fields")
        cache.delete(str(data1["required_fields"]))
        

        mycol = db.property_estate
        queryset= mycol.find({
            "broker_mobile":data1["broker_mobile"],
            })
        if len(queryset):
            serializer = EstateSerializer(queryset,many = True)
            jobject = json.dumps(serializer.data)
            cache.setex(name= data1["broker_mobile"], value=jobject, time=60*15)

        estate_sell =  [ _estate_ for _estate_ in list(queryset) if _estate_["estate_status"] in ["sell","sale"] ]
        jobject = json.dumps(estate_sell)
        if len(estate_sell):
            cache.setex(name= str(data1["broker_mobile"])+"sell", value=jobject, time=60*15)
        estate_buy =  [ _estate_ for _estate_ in list(queryset) if _estate_["estate_status"] in ["buy","purchase"] ]
        jobject = json.dumps(estate_buy)
        if len(estate_buy):
            cache.setex(name= str(data1["broker_mobile"])+"buy", value=jobject, time=60*15)
    except Exception as e:
        print("Unable to create caches key for estates")


@celery_app.task(bind=True, time_limit=2700)
def send_message_task(self,data,mobile_number,balance,mobile,findQuery):  
    mycol = db.property_estate
    queryset= mycol.find(findQuery,{ '_id': False})
    listestate =[]
    if queryset:
        listestate = list(queryset)
    interested = False
    if "," in mobile_number:
        interested = True
    no_of_messages = len(listestate)
    messageString = create_msg(listestate,interested,mobile)  
    response ={"error":""}    
    if "sms" in data and  data["sms"]:
        if "," in mobile_number:
            number_list = mobile_number.split(",")
            for mobile_agent in number_list:
                sms = send_sms(mobile_agent,messageString[0])
        else:
            sms = send_sms(mobile_number[0],messageString[0])
        response["sms"] = sms
        if not sms["success"]:
            response["error"] = "sms failed"
            response["success"] = False
        else:
            mycol = db.UserManagement_user
            updatestmt = (
                {"mobile":mobile},
                {"$set":{
                    "balance": balance - no_of_messages*50,
                    "is_premium": True,
                }}
            )
            broker = mycol.update_one(*updatestmt)
    if "whatsapp" in data and  data["whatsapp"]:
        if "," in mobile_number:
            number_list = mobile_number.split(",")
            for mobile_agent in number_list:
                whatsapp = send_whatsapp_msg(mobile_agent,messageString[0])
        else:
            whatsapp = send_whatsapp_msg(mobile_number[0],messageString[0])
        response["whatsapp"] = whatsapp
        if not whatsapp["success"]:
            response["error"] =response["error"] + "whatsapp failed"
            response["success"] = False
        else:
            mycol = db.UserManagement_user
            updatestmt = (
                {"mobile":mobile},
                {"$set":{
                    "balance": balance - no_of_messages*10,
                    "is_premium": True,
                }}
            )
            broker = mycol.update_one(*updatestmt)

    if interested:
        formal_message = "I am Interested"
        msg_data={
            "seen":False,
            "receiver_name":"BrokerBookAssitant",
            "description":formal_message
        }
        create_msg_in_db(msg_data,mobile)
        formal_message = "Thanks for using Broker Book our Broker will Connect you soon"
        send_whatsapp_msg(mobile,formal_message)
        msg_data={
                "seen":False,
                "receiver_name":mobile,
                "description":formal_message
            }
        create_msg_in_db(msg_data,"BrokerBookAssitant")
    else:
        msg_data={
            "seen":False,
            "receiver_name":mobile_number[0],
            "description":messageString[0]
        }
        create_msg_in_db(msg_data,mobile)