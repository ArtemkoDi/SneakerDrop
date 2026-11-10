from django.contrib import admin

from .models import Brand, Sneaker, SneakerSize

admin.site.register(Brand)
admin.site.register(Sneaker)
admin.site.register(SneakerSize)
