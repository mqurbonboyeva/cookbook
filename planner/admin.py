from django.contrib import admin

from .models import MealPlan, ShoppingItem

admin.site.register(MealPlan)
admin.site.register(ShoppingItem)