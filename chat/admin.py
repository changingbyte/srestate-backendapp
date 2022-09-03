from django.contrib import admin

from .models import Contacts, Messages
admin.site.register(Contacts)
admin.site.register(Messages)