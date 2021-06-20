from django.contrib import admin
from .models import Contest, SiteData, UserData, Profile,Team

# Register your models here.
admin.site.register(Contest)
admin.site.register(SiteData)
admin.site.register(UserData)
admin.site.register(Team)
admin.site.register(Profile)
