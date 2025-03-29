from django.contrib import admin
from .models import Product , Cart ,Cart_item,Transaction

admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Cart_item)
admin.site.register(Transaction)
# Register your models here.
