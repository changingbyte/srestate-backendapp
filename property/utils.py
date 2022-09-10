import uuid
from rest_framework.response import Response
from rest_framework import status
from property.message_mapping import MSG_MAPPING ,QUERY_MAPPING
import json
from django.http import JsonResponse

def check_balance(request,n):
    amount  = 0
    if "sms" in request.data and  request.data["sms"]:
        amount = amount +  50 * n
    if "whatsapp" in request.data and  request.data["whatsapp"]:
        amount = amount +  10 * n
    
    return amount

def create_msg(jobject,interested = False,user_mobile = None):
    msg_string = ""
    query_json =      {
            "type" :[],
            "estate_type" :[],
            "budget" :[],
            "area" :[]
            }
    for estate in jobject:
        if interested:
            msg_string = msg_string + f" \n \n {user_mobile} IS INTERESTED IN BELOW PROPERTY"
        if "estate_name" in estate:
            msg_string = msg_string + " \n \n" + str(estate["estate_name"]).upper()
        
        for attribute, value in estate.items():
            if attribute in MSG_MAPPING.keys() and value:
                msg_string = msg_string + " \n" + MSG_MAPPING[attribute] + " " + str(value)
            if attribute in QUERY_MAPPING.keys() and value:
                query_json[QUERY_MAPPING[attribute]].append(value)
        msg_string = msg_string + " \n"
        for key in query_json.keys():
            query_json[key] = list(set(query_json[key]))
        query_json["id"] = str(uuid.uuid4())
    return msg_string,query_json


def ReturnResponse(status,errors=[],data=[],msg="",success=False):
    response = {

        "success":success,
        "error":errors,
        "message":msg,
        "data":data,
    }
    return Response(data= response,status = status)


def ReturnJsonResponse(status,errors=[],data=[],msg="",success=False):
    if type(data) == str:
        data = json.loads(data)
    response = {

        "success":success,
        "error":errors,
        "message":msg,
        "data":data,
    }
    return JsonResponse(data= response,status = status)

