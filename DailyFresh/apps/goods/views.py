import os
from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from .models import Goods, GoodsCategory, IndexGoodsBanner, IndexPromotionBanner, IndexCategoryGoodsBanner, GoodsSKU
from django.core.cache import cache
from django_redis import get_redis_connection
from django.core.paginator import Page, Paginator


# Create your views here.

def index(request):
    context = cache.get('index')

    if context is None:
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

        cache.set('index', context, 3600)

    response = render(request, 'index.html', context)
    # html = response.content.decode()
    # with open(os.path.join(settings.GENERATE_HTML, 'index.html'), 'w') as f:
    #     f.write(html)

    return response


def list(request, category_id):
    try:
        category_now = GoodsCategory.objects.get(pk=category_id)
    except:
        raise Http404
    # 当前分类的所有商品
    sku_list = GoodsSKU.objects.filter(category_id=category_id).order_by('-id')
    # 查询所有分类
    category_list = GoodsCategory.objects.all()
    # 查询当前类的前两个商品
    new_list = category_now.goodssku_set.all().order_by('-id')[0:2]

    paginator = Paginator(sku_list, 1)
    page = paginator.page(1)
    context = {
        'title': '商品列表',
        'page': page,
        'category_list': category_list,
        'category_now': category_now,
        'new_list': new_list,

    }
    return render(request, 'list.html', context)


def detail(request, sku_id):
    try:
        sku = GoodsSKU.objects.get(pk=sku_id)
    except:
        raise Http404()

    category_list = GoodsCategory.objects.all()

    new_list = sku.category.goodssku_set.all().order_by('-id')[0:2]

    other_list = sku.goods.goodssku_set.all()

    redis_client = get_redis_connection()
    key = 'history%d' % request.user.id
    redis_client.lrem(key, 0, sku_id)
    redis_client.lpush(key, sku_id)
    if redis_client.llen(key) > 5:
        redis_client.rpop(key)

    context = {
        'title': '商品详情',
        'sku': sku,
        'category_list': category_list,
        'new_list': new_list,
        'other_list': other_list,

    }

    return render(request, 'detail.html', context)
