# library_management_system/accounts/admin.py

from django.contrib import admin
from .models import CustomUser

admin.site.register(CustomUser)