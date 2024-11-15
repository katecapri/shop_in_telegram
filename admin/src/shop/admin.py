import logging
from django.contrib import admin
from . import models
from . import forms

logger = logging.getLogger('app')


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_per_page = 30


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_per_page = 30
    form = forms.CategoryFrom


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_per_page = 30
    form = forms.ProductFrom


@admin.register(models.CartProduct)
class CartProductAdmin(admin.ModelAdmin):
    list_per_page = 30


@admin.register(models.FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_per_page = 30