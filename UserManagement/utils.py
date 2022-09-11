from random import random
from venv import create
from django.contrib.auth import authenticate , login
from UserManagement.serializers import User
from rest_framework import serializers
from UserManagement.models import BrokersUsers ,User
from srestate.settings import TWILIO_AUTH_TOKEN ,TWILIO_ACCOUNT_SID
from twilio.rest import Client
import random
from property.estate.estate_serializers import EstateSerializer,EsateRealtedObjectSerilaizer
from datetime import datetime



# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure

def read_json_related(findQuery):
    budget=1000000
    floor_space =1000000
    number_of_bedrooms =0
    estate_status = ""
    if "estate_type" in findQuery.keys():
        estate_type = findQuery["estate_type"]
        if not isinstance(estate_type,list):
            findQuery["estate_type"] = [estate_type]
    if "area" in findQuery.keys():
        area = findQuery["area"]
        if not isinstance(area,list):
            findQuery["area"] = [area]
    else:
        findQuery["area"] = []
    if "estate_status" in findQuery.keys():
        if isinstance(findQuery["estate_status"],list):
            findQuery["estate_status"] = findQuery["estate_status"][0]
        if findQuery["estate_status"] in ["sell"]:
            estate_status = ["purchase" ,"buy"]
        elif findQuery["estate_status"] in ["purchase","buy"]:
            estate_status =  ["sell"]
        elif findQuery["estate_status"] == "rent":
            estate_status = ["rent"] 
            if findQuery["rent_status"] == "available":
                findQuery["rent_status"] = "required"
            else:
                findQuery["rent_status"] = "available"
    if "budget" in findQuery.keys():
        budget = findQuery["budget"]
        if isinstance(budget,list):
            budget.sort()
            budget = budget[-1]
        budget = float(str(budget))*1.1
    if "floor_space" in findQuery.keys():
        floor_space = findQuery["floor_space"]
        if isinstance(floor_space,list):
            floor_space.sort()
            floor_space = floor_space[-1]
        floor_space = float(str(floor_space))*1.1
    if "number_of_bedrooms" in findQuery.keys():
        number_of_bedrooms = findQuery["number_of_bedrooms"]
        if not isinstance(number_of_bedrooms,list):
            number_of_bedrooms = [number_of_bedrooms]

    return findQuery,number_of_bedrooms,budget,floor_space,estate_status


def find_related_db(mycol,findQuery):
    budget=1000000
    floor_space =1000000
    number_of_bedrooms = 0
    findQuery,number_of_bedrooms,budget,floor_space,estate_status = read_json_related(findQuery)
    
    print(findQuery,number_of_bedrooms,budget,floor_space,estate_status)
    custom_filter_list = []
    if "rent_status" in findQuery:
        custom_filter_list.append({"rent_status":findQuery["rent_status"]})
    if "broker_mobile" in findQuery:
        custom_filter_list.append({ "broker_mobile": findQuery["broker_mobile"] })
    if "area"  in findQuery and findQuery["area"]:
        custom_filter_list.append({ "area": {"$in" :findQuery["area"] }})
    if "estate_type" in findQuery:
        custom_filter_list.append({ "estate_type": {"$in" :findQuery["estate_type"] }})
    if "estate_status" in findQuery:
        custom_filter_list.append({ "estate_status": {"$in":estate_status} })
    if number_of_bedrooms:
        custom_filter_list.append({ "number_of_bedrooms": {"$in":number_of_bedrooms} })


    print(custom_filter_list)
    
    queryset= mycol.aggregate([
        {
            "$match" : {"$and": [{ "id": {"$ne":findQuery["id"]} }] +
                [
                    {"$or": [
                    {"$or" : [ { "floor_space": {"$lte": floor_space } }]},
                    {"$or" :[{ "budget": {"$lte": budget } }]}
                ]}

                ] + custom_filter_list
                

                } } ]
        )
    serilizer = EsateRealtedObjectSerilaizer(data=list(queryset),many=True)
    if serilizer.is_valid():
        return serilizer.data
    else:
        print(serilizer.errors)
        return []
    # print(list(queryset))
    # if list(queryset):
    #     print("here")
        
        
    # else:
    #     return  []

def send_whatsapp_msg(mobile,messageString):
    try:
        print(messageString)
        account_sid = TWILIO_ACCOUNT_SID
        auth_token = TWILIO_AUTH_TOKEN
        client = Client(account_sid, auth_token) 
        print(messageString)
        message = client.messages.create( 
                                    from_='whatsapp:+14155238886',  
                                    body=messageString,
                                    to=f'whatsapp:+91{mobile}' 
                                ) 
        
        print(message.sid)
        msg_status= {}
        msg_status["success"] = True
        msg_status["msg"] = "Success"
        return msg_status
    except Exception as e:
        msg_status= {}
        msg_status["success"] = False
        msg_status["msg"] = str(e)
        print(msg_status)
        return msg_status



def send_otp(mobile, appString):
    try:
        account_sid = TWILIO_ACCOUNT_SID
        auth_token = TWILIO_AUTH_TOKEN
        client = Client(account_sid, auth_token)
        OTP = str(random.randint(100000,999999))
        print(OTP)
        message = client.messages \
                        .create(
                            body=f"SR ESTATE for OTP for Verification  {appString}  {OTP}",
                            from_='+19715715369',
                            to=f'+91{mobile}'
                        )
        print(message.sid)
        return OTP
    except Exception as e:
        print(e)
        return 123456

def send_sms(mobile,messageString):
    try:
        account_sid = TWILIO_ACCOUNT_SID
        auth_token = TWILIO_AUTH_TOKEN
        client = Client(account_sid, auth_token)
        message = client.messages \
                        .create(
                            body=messageString,
                            from_='+19715715369',
                            to=f'+91{mobile}'
                        )
        print(message.sid)
        msg_status= {}
        msg_status["success"] = True
        msg_status["msg"] = "Success"
        return msg_status
    except Exception as e:
        msg_status= {}
        msg_status["success"] = False
        msg_status["msg"] = str(e)
        return msg_status



def get_and_authenticate_user(Mobile, otp):
    user = authenticate(Mobile=Mobile, otp=otp)
    return user

def create_user_account(Mobile,appString):
    otp =send_otp(mobile = Mobile, appString=appString)
    #otp = 123456
    
    try:
        user= User.objects.get(
            username = str(Mobile)
        )
        user.otp= otp
        user.last_login = datetime.now()
        user.save()
        
        return user , False
    except User.DoesNotExist:
        user = User.objects.create(
        username = str(Mobile),
        is_superuser = False,
        password = str(Mobile*2),
        first_name = " ",
        last_name = " ",
        is_active = True,
        )
        user.otp = otp
        user.mobile = Mobile
        user.last_login = datetime.now()
        user.save()
        return user, True