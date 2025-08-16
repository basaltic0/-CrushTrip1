from django.contrib import admin
from .models import CartItem
from .models import crawlers_main
from .models import CustomUser

admin.site.register(CartItem)
admin.site.register(crawlers_main)
admin.site.register(CustomUser)
# Register your models here.
