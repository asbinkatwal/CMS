from django.contrib import admin
from django.contrib.auth import get_user_model 
from .models import menu ,Vote


User = get_user_model()

admin.site.register(User)
admin.site.register(menu)

class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'menu') 
    list_filter = ('user', 'menu')  
    
    search_fields = ('user__username', 'menu__date')  

admin.site.register(Vote , VoteAdmin)
