"""
Django admin cutomization
"""
from django.contrib import admin
from user import models as UserModels


admin.site.register(UserModels.User)



