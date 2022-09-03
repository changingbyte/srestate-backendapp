from django.urls import path

from property.location import location_views as views

urlpatterns = [
    path("city/",views.ListCityAPIView.as_view(),name="city_list"),
    path("city/create/", views.CreateCityAPIView.as_view(),name="city_create"),
    path("city/update/<int:pk>/",views.UpdateCityAPIView.as_view(),name="update_city"),
    path("city/delete/<int:pk>/",views.DeleteCityAPIView.as_view(),name="delete_city"),
    path("area/",views.ListAreaAPIView.as_view(),name="area_list"),
    path("area/create/", views.CreateAreaAPIView.as_view(),name="area_create"),
    path("area/update/<int:pk>/",views.UpdateAreaAPIView.as_view(),name="update_area"),
    path("area/delete/<int:pk>/",views.DeleteAreaAPIView.as_view(),name="delete_area"),
	path("apartment/",views.ListApartmentAPIView.as_view(),		  		  name="apartment_list"),
    path("broker/create/", views.CreateBrokerAPIView.as_view(),		  name="broker_create"),
    path("brokerDetails/",views.get_broker_profile, name="broker_detail"),
    path("get_balance/", views.get_balance,name="broker_balance"),
    path("apartment/create/", views.CreateApartmentAPIView.as_view(),		  name="apartment_create"),
    path("apartment/blukcreate/", views.CreateBulkApartmentAPIView.as_view(),		  name="apartment_bulk_create"),
    path("apartment/update/<int:pk>/",views.UpdateApartmentAPIView.as_view(),name="update_apartment"),
    path("apartment/delete/<int:pk>/",views.DeleteApartmentAPIView.as_view(),name="delete_apartment")

]