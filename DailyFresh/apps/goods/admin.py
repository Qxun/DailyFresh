import os
import time
from django.conf import settings
from django.contrib import admin
from django.core.cache import cache
from django.shortcuts import render
from .models import GoodsCategory, Goods, GoodsImage, GoodsSKU, IndexGoodsBanner, IndexCategoryGoodsBanner, \
    IndexPromotionBanner
from celery_tasks.tasks import generate_html


# Register your models here.
# class GoodsCategoryAdmin(admin.ModelAdmin):
class BaseAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        generate_html.delay()
        cache.delete('index')

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        generate_html.delay()
        cache.delete('index')


class GoodsCategoryAdmin(BaseAdmin):
    pass


class IndexCategoryGoodsBannerAdmin(BaseAdmin):
    pass


class IndexPromotionBannerAdmin(BaseAdmin):
    pass


class IndexGoodsBannerAdmin(BaseAdmin):
    pass





admin.site.register(GoodsCategory, GoodsCategoryAdmin)
admin.site.register(Goods)
admin.site.register(GoodsSKU)
admin.site.register(GoodsImage)
admin.site.register(IndexCategoryGoodsBanner, IndexCategoryGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
