from django.contrib import admin

from .models import Category, ConsultantGroup, ConsultantGroupItem, Product

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ConsultantGroup)
admin.site.register(ConsultantGroupItem)
