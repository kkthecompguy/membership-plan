from django.contrib import admin
from .models import UserMembership, Subscription, Membership

admin.site.register(Membership)
admin.site.register(UserMembership)
admin.site.register(Subscription)
