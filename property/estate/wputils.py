import re
import json
from property.location.location_views import db
from srestate.config import CACHES
from property.models import Estate
import redis

cache = redis.Redis(
    host=CACHES["default"]["host"],
    port=CACHES["default"]["port"], 
    password=CACHES["default"]["password"])

required_fields = {
    "area":[],
    "estate_status":[],
    "apartment":[],
    "furniture":["WITH FULL FURNITURE", "Full Furnished" ,"naked","Fully Furnished","Semi Furnished","luxurious furnished","furnished","Renovated"],
    "property_type":[],
}

mapping_db = {
    "area":["area_name",db.property_area.find({},{"area_name":1,"_id":0})],
    "estate_status":["estate_status_name",db.property_estatestatus.find({},{"estate_status_name":1,"_id":0})],
    "apartment":["apartment_name",db.property_apartment.find({},{"apartment_name":1,"_id":0})],
    "property_type":["type_name",db.property_estatetype.find({},{"type_name":1,"_id":0})]
}

def findOptimized(required_fields,mapping_db):
    if "required_fields" in cache:
        return json.loads(cache.get("required_fields"))

    for key,value  in mapping_db.items(): 
        required_fields[key] = [ x[value[0]].lower() for x in   list(value[1]) ]
    jobject = json.dumps(required_fields)
    cache.setex(name= "required_fields", value=jobject, time=60*60)
    return required_fields


def checkisdigit(inputstring):
    if False in [char.isdigit()  for char in inputstring]:
        return False
    else:
        return True


def findMobile(inputstring):
    pattern = re.compile(r"\d{10}")
    if re.search(pattern=pattern, string=inputstring) :
        return re.findall(pattern=pattern,string= inputstring)
    else:
        return []

def findBigNumbers(inputstring):
    pattern = re.compile(r"[1-9]\d{3,10}")
    if re.search(pattern=pattern, string=inputstring) :
        numbers = re.findall(pattern=pattern,string= inputstring)
        numbers = [int(x) for x in numbers]
        return numbers
    else:
        return []

def find_match(SizeInput,size_matches):
    if size_matches[0] in SizeInput:
        return SizeInput
    sizelist = SizeInput.split(" ")
    matches = []
    mul =1
    for i in sizelist:
        print(i,"i")
        if checkisdigit(i) and len(i) :
            matches.append(float(i))
        
        elif any(x in i for x in ["lk","lac","lakh","lak","lacs","lakhs"]):
            index_c = i.find(next(filter(str.isalpha, i)))
            if index_c:
                matches.append(float(i[:index_c]))
            mul = 100000
        elif any(x in i for x in ["cr"]):
            index_c = i.find(next(filter(str.isalpha, i)))
            if index_c:
                matches.append(float(i[:index_c]))
            mul = 10000000
    print(matches)
    if len(matches):
        
        return matches[0]*mul


def findOwner(input):
    pattern = re.compile(r"\d{5}[-\.\s]??\d{5}")
    pattern2 = re.compile(r"\d{1,2}:\d{2}\s['am]','pm]']")
    pattern1 = re.compile(r"\d{2}/\d{2}")

    if (re.search(pattern=pattern1, string=input) and re.search(pattern=pattern2, string=input)) or re.search(pattern=pattern, string=input) :
        mobiles = re.findall(pattern=pattern,string=input)

        return True,mobiles[0].replace(" ","")
    else:
        return False,False


def cleaningLine(i):
    i = i.replace("/"," ")
    if i != "\n":
        i= i.strip()
        i = i.rstrip(",.\n")
        i= i.strip()
        i = i.rstrip(",.\n")
        i = i.lstrip("👉 ")
        i = i.lstrip("👉🏻")
        i = i.lstrip("*👉🏻")
        i = i.lstrip("🏻☎☎☎☎")
        i = i.lstrip("*♦️")
        #print(i)
    for k in i:
        fv = ["*",",","@","-","=","\ud83d\udc49\ud83c\udffb"]
        if k in fv:
            i = i.replace(k,"")
        if "sqft" in i.lower():
            i = i.replace(":","")
    
    return i

def findHouse(input):
    pattern = re.compile(r"\d{1}[-\.\s\,][-\.\s\,]}\d{0,1}[-\.\s]??\D{8}|\d{1,6}\D{3,20}|\d{1,6}[,\.]\d{1,6}[,\.]\s{0,1}\D{1,10}|\d{1,6}[,\.]\s{0,1}\D{1,10}")
    #pattern = re.compile(r"|\d{3}[-\.\,\s]{2}??\D{4,5}")
    houselist = re.findall(pattern=pattern, string=input)
    false_values = ["+", ":","pm]","am]"]
    filterhouse = []
    for i in false_values:
        filterhouse = filterhouse + [ x for x in houselist if i  in x  ]
    return set(houselist)- set(filterhouse)


def removeX(input):
    i =input
    x_ind = -1
    x_list = [" X "," × ", "X","x","×"]
    for x in x_list:
        if x in i:
            #print(x)
            x_ind = i.find(x)
            if " " in x:
                i = i.replace(x,x.strip())
                #print(i)
                x_ind = i.find(x.strip())
                #print(x_ind)

    if x_ind != -1:
        s_index = i[:x_ind].rfind(" ")
        s1_index = i[x_ind:].find(" ")
        #print(s_index,s1_index)
        if(s_index !=-1):
            n1 = i[s_index:x_ind].strip()
        else:
            n1 = i[:x_ind].strip()
        if(s1_index ==-1):
            n2 = i[x_ind+1:].strip()
        else:
            n2 = i[x_ind+1:x_ind+s1_index].strip()
        
        if n1.isdigit() and n2.isdigit():
            mul = int(n1) * int(n2)
            return mul
    return None

def filterRooms(mydict):
    room_list = []
    for j,i in enumerate(mydict["number_of_bedrooms"]):
        bhk_index = i.find("bhk")
        if bhk_index!= -1:
            mydict["number_of_bedrooms"][j]  = i[:bhk_index]
            mydict["number_of_bedrooms"][j] = mydict["number_of_bedrooms"][j].replace(" ","")
            room_list.append(int(mydict["number_of_bedrooms"][j]))

        else:
            size_matches = ["Sq. Yards" ,"sq yard","Sq yards","sq","carpet","ft","Sf","SFT","SB","SQFT","var", "Square","feet","vaar","VINGA"]
            size_matches = [ x.lower() for x in size_matches ]
            price_matches = ["lk","Lac","lakh", "cr","lak","lacs"]
            price_matches = [ x.lower() for x in price_matches ]
            
            
            if any(x in mydict["number_of_bedrooms"][j] for x in size_matches):
                size_match = find_match(mydict["number_of_bedrooms"][j],size_matches)
                if "floor_space" in mydict.keys():
                    mydict["floor_space"].append(size_match)
                else:
                    mydict["floor_space"] = [size_match]
        
            elif any(x in mydict["number_of_bedrooms"][j] for x in price_matches):
                if "budget" in mydict.keys():
                    mydict["budget"].append(find_match(mydict["number_of_bedrooms"][j],price_matches))
                else:
                    mydict["budget"] = [find_match(mydict["number_of_bedrooms"][j],price_matches)]
                
            else:
                if "others" in mydict.keys():
                    mydict["others"].append(mydict["number_of_bedrooms"][j])
                else:
                    mydict["others"] = [mydict["number_of_bedrooms"][j]]
    print("room_list",room_list)
    mydict["number_of_bedrooms"] = room_list

def filterOthers(mydict):
    if "others" in mydict.keys():
        for j,i in enumerate(mydict["others"]):
            if findBigNumbers(mydict["others"][j]) :
                if "budget" in mydict.keys():
                    mydict["budget"] + findBigNumbers(mydict["others"][j])
                else:
                    mydict["budget"] = findBigNumbers(mydict["others"][j])
            if findPropertyType(mydict["others"][j]):
                if "estate_type" in mydict.keys():
                    mydict["estate_type"] + findBigNumbers(mydict["others"][j])
                else:
                    mydict["estate_type"] = findBigNumbers(mydict["others"][j])


def findSize(input):
    pattern = re.compile(r"\d{1,4}\s{0,1}[X,x,×]\s{0,1}\d{1,4}")
    #pattern = re.compile(r"|\d{3}[-\.\,\s]{2}??\D{4,5}")
    sl = re.findall(pattern=pattern, string=input)
    filtersl = []
    for i in sl:
        if removeX(i) is not None:
            filtersl.append(removeX(i))
    return filtersl

def findBudget(input):
    keywords=["lk","Lac","lakh", "cr"]
    inputlist = input.split(" ")
    typelist = []
    keywords = [ x.lower() for x in keywords ]
    for i in keywords:
        if i in inputlist:
            typelist.append(i)
    return typelist

def findType(input):
    keywords=["purchase","rent","buy", "sell","sale"]
    inputlist = input.split(" ")
    typelist = []
    for i in keywords:
        if i in inputlist:
            if i in ["sale","sell"]:
                typelist.append("sell")
            elif i in ["purchase","buy"]:
                typelist.append("buy")
            else:
                typelist.append(i)
    
    return typelist

#societylist = apartment.objects.all()
# societylist = ["Royal Paradise","Keshav Narayan","Raj Harmoney","Grandza","Rayaltone","Sun Sine Residency","Anupam hieght","Dev bhoomi","Sns splendid","Hitek Avenue","Surya green view","Next orchied","Veer exotica","CAPITAL GREENS","ECO GARDEN","SANGINI","OFIRA RESIDENCY" ,"RAJHANS","Srungal Solitaire","Rajhans Royalton","utsav","meera","marvela","Aakash expression","SURYA PRAKASH RESIDENCY",
# "NISRAG AAPRMENT","RAJTILAK AAPRMENT","SURYA PLEASE","AARNAV APRMENT","SURYA DARSAN","KPM RESIDENCY","MURTI RESIDENCY","FALCAN AVENUE","AASHIRWAD PARK","GOLDEN AVENUE","PADMA KURTI","SHIMANDAR APPRMENT" ,"BAGVTI ASHISH" ,"MEGNA PARK","SHITAL PARK","NAVPAD AAPRMENT" ,"SURYA COMPLEX" ,"PALACIO","KESHAV NARAYNA","OPERA HOUSE","AARJAV AAPRMENT","MAAHI RESIDENCY","MAGH SHARMAND","SAKAR RESIDENCY","MURLIDHAR","SANGINI RESIDENCY"]
rf =  findOptimized(required_fields,mapping_db)
societylist = rf["apartment"]


def findArea(input):
    inputlist = input.split(" ")
    keywords = [ x.lower() for x in rf["area"] ]
    typelist = []
    for i in keywords:
        if i in inputlist or i in input:
            typelist.append(i)
    
    return typelist


def findSociety(input):
    inputlist = input.split(" ")
    keywords = [ x.lower() for x in rf["apartment"] ]
    typelist = []
    for i in keywords:
        # so = fuzz.ratio(i,inputlist)
        if i in inputlist or i in input:
            typelist.append(i)
    
    return typelist

def findFurntiure(input):
    keywords=["WITH FULL FURNITURE", "Fully Furnished","Semi Furnished","luxurious furnished","furnished","Renovated"]
    inputlist = input.split(" ")
    typelist = []
    keywords = [ x.lower() for x in keywords ]
    for i in keywords:
        if i in inputlist or i in input:
            typelist.append(i)
            break
    return typelist

def findPropertyType(input):
    inputlist = input.split(" ")
    #print(inputlist)
    typelist = []
    keywords = [ x.lower() for x in rf["property_type"] ] +["office"]
    for i in keywords:
        if i in inputlist or i in input:
            typelist.append(i)
            break
    return typelist 

def findRentKeyword(input):
    inputlist = input.split(" ")
    #print(inputlist)
    typelist = []
    keywords = [ "available","required"]
    for i in keywords:
        if i in inputlist or i in input:
            typelist.append(i)
            break
    return typelist    

def findALlRequiremnts(lines,start_index):
    myDict = dict()
    prevHouse = start_index

    myDict[start_index] = dict()
    for j,i in enumerate(lines[start_index:]):
        #print(prevHouse,j,start_index,i)
        if findOwner(i) and j != 0:
            #myDict[prevHouse]["Newquery"] = "true"
            return myDict[prevHouse], start_index+j
        else:
            i= cleaningLine(i).lower() 
            #print(len(findArea(i)) , len(findType(i)) , find_house ,len(findPropertyType(i)), findSociety(i))
            if i == "\n":
                #print("blank")
                prevHouse = start_index+j
                myDict[prevHouse] = dict()
                    

            else:
                find_area = findArea(i)
                find_type = findType(i)
                find_house = findHouse(i)
                print(find_house)
                find_property_type = findPropertyType(i)
                find_society = findSociety(i)
                find_mobile = findMobile(i)
                find_size = findSize(i)
                find_furniture = findFurntiure(i)
                find_rent_keyword = findRentKeyword(i)

                if len(find_area) or  len(find_type) or len(find_house) or len(find_property_type) or len(find_society) or len(find_mobile) :
                    if len(find_house):
                        if "number_of_bedrooms" in myDict[prevHouse].keys():
                            myDict[prevHouse]["number_of_bedrooms"] = myDict[prevHouse]["number_of_bedrooms"]+ list(find_house)
                        else:
                            myDict[prevHouse]["number_of_bedrooms"] = list(find_house)
                    if "area" in myDict[prevHouse].keys():
                        myDict[prevHouse]["area"] = myDict[prevHouse]["area"]+find_area
                    elif len(find_area):
                        myDict[prevHouse]["area"] = find_area
                    
                    if "estate_status" in myDict[prevHouse].keys():
                        myDict[prevHouse]["estate_status"] = myDict[prevHouse]["estate_status"]+find_type
                    elif len(find_type):
                        myDict[prevHouse]["estate_status"] = find_type
                    
                    if "apartment" in myDict[prevHouse].keys():
                        myDict[prevHouse]["apartment"] = myDict[prevHouse]["apartment"]+find_society
                    elif len(find_society):
                        myDict[prevHouse]["apartment"] = find_society

                    if "estate_type" in myDict[prevHouse].keys():
                        myDict[prevHouse]["estate_type"] = myDict[prevHouse]["estate_type"]+find_property_type
                    elif len(find_property_type):
                        myDict[prevHouse]["estate_type"] = find_property_type
                    
                    if "rent_status" in myDict[prevHouse].keys():
                        myDict[prevHouse]["rent_status"] = myDict[prevHouse]["rent_status"]+find_rent_keyword
                    elif len(find_rent_keyword):
                        myDict[prevHouse]["rent_status"] = find_rent_keyword
                    
                    if "broker_mobile" in myDict[prevHouse].keys():
                        myDict[prevHouse]["broker_mobile"] = myDict[prevHouse]["broker_mobile"]+find_mobile
                    elif len(find_mobile):
                        myDict[prevHouse]["broker_mobile"] = find_mobile
                        myDict[prevHouse]["endquery"] = "true"
                    
                    if len(find_size):
                        if "floor_space" in myDict[prevHouse].keys():
                            myDict[prevHouse]["floor_space"] = myDict[prevHouse]["floor_space"]+ list(find_size)
                        else:
                            myDict[prevHouse]["floor_space"] = list(find_size)

                    if len(find_furniture):
                        myDict[prevHouse]["furniture"] = find_furniture
                else:
                    if "others" in myDict[prevHouse].keys():
                        myDict[prevHouse]["others"].append(i)
                    else:
                        myDict[prevHouse]["others"] = [i]
    return myDict[prevHouse], start_index+j

def filterSize(mydict):
    if "number_of_bedrooms" in mydict.keys():
        mydict["number_of_bedrooms"] = [ x.lower() for x in mydict["number_of_bedrooms"] ]
        filterRooms(mydict)
        print(mydict)
    if "others" in mydict.keys():
        filterOthers(mydict)
    return mydict
    


def get_data_from_msg(string,mobile,multi= False):

    print(string)
    # estate_parameters = ["estate_type","estate_status","area","number_of_bedrooms","budget","apartment","floor_space","furniture"]
    estate_parameters = ["estate_type","estate_status","area"]
    lines  = [line for line in string.split("\n") if line.strip() != '']
    i=0
    owner = mobile
    new_dic = dict()
    json_index = []
    estate_list =[]
    estate = {}
    pre_estate = {}
    while i < len(lines):
        if lines[i] == "\n":
            i=i+1
        else:
            json_index = findALlRequiremnts(lines,i)
            print(estate,i)

            if set(estate_parameters).issubset(set(list(estate.keys()))):
                if "apartment" not in estate.keys():
                    estate["apartment"] = "any"
                if "number_of_bedrooms" not in estate.keys():
                    estate["number_of_bedrooms"] = 0
                if "floor_space" not in estate.keys():
                    estate["floor_space"] = 0
                if "budget" not in estate.keys():
                    estate["budget"] = 0
                print(2)
                estate_list.append(estate)
                estate = filterSize(json_index[0])
            # elif set(estate_parameters).issubset(set(list(pre_estate.keys()))):
            #     if "apartment" not in pre_estate.keys():
            #         pre_estate["apartment"] = "any"
            #     if "number_of_bedrooms" not in pre_estate.keys():
            #         pre_estate["number_of_bedrooms"] = 0
                
            #     if "floor_space" not in pre_estate.keys():
            #         pre_estate["floor_space"] = 0

            #     print(1)
            #     estate_list.append(pre_estate)
            #     pre_estate ={}
            # elif list(estate.keys()) and list(pre_estate.keys()):
            #     print(3)
            #     if set(list(pre_estate.keys())).issubset(set(list(estate.keys()))) or  set(list(estate.keys())).issubset(set(list(pre_estate.keys()))):
            #         if "apartment" not in pre_estate.keys():
            #             pre_estate["apartment"] = "any"
            #         if "number_of_bedrooms" not in pre_estate.keys():
            #             pre_estate["number_of_bedrooms"] = 0
                    
            #         if "floor_space" not in pre_estate.keys():
            #             pre_estate["floor_space"] = 0

            #         estate_list.append(pre_estate)
            #         pre_estate ={}
                    
            #     pre_estate.update(estate)
            #     estate = filterSize(json_index[0])
            #     estate.update(json_data)
            else:
                # print(4)
                json_data = filterSize(json_index[0])
                estate.update(json_data)
        i = i+1
    print(estate)
    if not estate_list:
        print("here")
        if multi:
            return False
        return estate
        # if "apartment" not in estate.keys():
        #     estate["apartment"] = "any"
        # if "number_of_bedrooms" not in estate.keys():
        #     estate["number_of_bedrooms"] = 0
        # if "floor_space" not in estate.keys():
        #     estate["floor_space"] = 0
        # if "budget" not in estate.keys():
        #     estate["budget"] = 0
        # estate["broker_mobile"] = mobile
        # estate_list.append(estate)

    json_object = json.dumps(estate_list, sort_keys=True, indent = 4) 
    with open("samplequery2.json", "w") as outfile:
        outfile.write(json_object)
    new_list =[]
    if multi:
        for data in estate_list:
            new_data ={}
            for key in data:
                if isinstance(data[key],list) and data[key]:
                    new_data[key] = data[key][0]
                else:
                    new_data[key] = data[key]
            new_data["society"] = new_data["apartment"]
            if "rent_status" in new_data and new_data["estate_status"] in ["sell","buy"]:
                new_data.pop("rent_status")
            if "others" in new_data:
                new_data.pop("others")
            if "endquery" in new_data:
                new_data.pop("endquery")
            if "number_of_bedrooms" in new_data:
                if not new_data["number_of_bedrooms"]:
                    new_data["number_of_bedrooms"] =0

            new_data["city"] ="surat"
            new_data["broker_name"] = mobile
            new_data.pop("apartment")
            new_data["broker_mobile"] = mobile

            print
            new_list.append(new_data)

            estate = Estate.objects.create(**new_data)
    if multi:
        return new_list
    return estate_list[0]

#print(jsonlist)

