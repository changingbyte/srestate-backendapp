
# def update_every_estate_name(request):
#     mycol = db.property_estate
#     data = mycol.find({})
#     for estate in list(data):
#         updatestmt = (
#             {"id":estate["id"]},
#             {"$set":{
#                 "estate_name": get_estate_name(estate),
#             }}
#         )
#         update_estate = mycol.update_one(*updatestmt)
#         print(update_estate.modified_count)