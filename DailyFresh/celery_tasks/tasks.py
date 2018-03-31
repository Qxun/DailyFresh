import os
from celery import Celery
from django.conf import settings
from django.shortcuts import render
from goods.models import GoodsCategory, IndexGoodsBanner, IndexPromotionBanner, IndexCategoryGoodsBanner
import time

app = Celery('celery_tasks.tasks', broker='redis://127.0.0.1:6379/6')


@app.task
def generate_html():
    time.sleep(2)
    category_list = GoodsCategory.objects.all()
    banner_list = IndexGoodsBanner.objects.all().order_by('index')
    promotion_list = IndexPromotionBanner.objects.all().order_by('index')

    for category in category_list:
        category.title_list = IndexCategoryGoodsBanner.objects.filter(display_type=0, category=category).order_by(
            'index')[0:3]
        category.img_list = IndexCategoryGoodsBanner.objects.filter(display_type=1, category=category).order_by(
            'index')[0:4]

    context = {
        'title': '首页',
        'category_list': category_list,
        'banner_list': banner_list,
        'promotion_list': promotion_list,
    }

    response = render(None, 'index.html', context)
    html = response.content.decode()
    with open(os.path.join(settings.GENERATE_HTML, 'index.html'), 'w') as f:
        f.write(html)
