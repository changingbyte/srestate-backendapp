from django.urls import path,include

from property.estate import estate_views as views
from property.views import  Broker_Page

urlpatterns = [
    path("",include("property.estate.urls")),
    path("",include("property.location.urls")),
    path('page/<str:mobile>/', Broker_Page.as_view(), name='broker_page'),

]