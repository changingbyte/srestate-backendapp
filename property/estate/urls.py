from django.urls import path, re_path

from property.estate import estate_views as views

urlpatterns = [
    path("estate/",views.ListEstateAPIView.as_view(),name="eststate_list"),
    path("estate/buy/",views.get_buy_estate,name="estate_buy_list"),
    path("estate/sell/",views.get_sell_estate,name="estate_sell_list"),
    path("estate/filter_query/",views.get_filter_estate,name="estate_filter_list"),
    path("estate/filter_details/",views.get_filter_details,name="estate_filter_details"),
    path("estate/create/", views.CreateEstateAPIView.as_view(),name="estate_create"),
    path("estate/sendmessage/",views.send_message,name="estate_send_message"),
    path("estate/details/<int:pk>/",views.estate_details,name="estate_details"),
    path("estate/update/<int:pk>/",views.UpdateEstateAPIView.as_view(),name="update_estate"),
    path("estate/delete/<int:pk>/",views.DeleteEstateAPIView.as_view(),name="delete_estate"),
    path("estate_status/",views.ListEstateStatusAPIView.as_view(),name="estate_status_list"),
    path("estate_status/create/", views.CreateEstateStatusAPIView.as_view(),name="estate_status_create"),
    path("estate_status/update/<int:pk>/",views.UpdateEstateStatusAPIView.as_view(),name="update_estate_status"),
    path("estate_status/delete/<int:pk>/",views.DeleteEstateStatusAPIView.as_view(),name="delete_estate_status"),
	path("estate_type/",views.ListEstateTypeAPIView.as_view(),		  		  name="estate_type_list"),
    path("estate_type/create/", views.CreateEstateTypeAPIView.as_view(),		  name="estate_type_create"),
    path("estate_type/update/<int:pk>/",views.UpdateEstateTypeAPIView.as_view(),name="update_estate_type"),
    path("estate_type/delete/<int:pk>/",views.DeleteEstateTypeAPIView.as_view(),name="delete_estate_type"),
    path("estate/createbywp/", views.get_data_from_wp , name="estate_create_by_whatsapp"),
    path("estate/get_related_property/", views.related_properties , name="estate_get"),
    # path("demo-reply", views.demo_reply),
    # path("update_estate_name/", views.update_every_estate_name)
    
]