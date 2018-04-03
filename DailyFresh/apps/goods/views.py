import json
import os
from django.conf import settings
from django.http import Http404
from django.shortcuts import render

from utils.page_list import get_page_list
from .models import Goods, GoodsCategory, IndexGoodsBanner, IndexPromotionBanner, IndexCategoryGoodsBanner, GoodsSKU
from django.core.cache import cache
from django_redis import get_redis_connection
from django.core.paginator import Page, Paginator
from haystack.generic_views import SearchView




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

    context['total_count']=get_cart_total(request)

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
    order = int(request.GET.get('order', 1))
    if order == 2:
        order_by = '-price'
    elif order == 3:
        order_by = 'price'
    elif order == 4:
        order_by = '-sales'
    else:
        order_by = '-id'

    # 当前分类的所有商品
    sku_list = GoodsSKU.objects.filter(category_id=category_id).order_by(order_by)
    # 查询所有分类
    category_list = GoodsCategory.objects.all()
    # 查询当前类的前两个商品
    new_list = category_now.goodssku_set.all().order_by('-id')[0:2]

    paginator = Paginator(sku_list, 1)
    total_page = paginator.num_pages
    # 接收页码值，进行判断
    pindex = int(request.GET.get('pindex', 1))
    if pindex < 1:
        pindex = 1
    if pindex > total_page:
        pindex = total_page
    page = paginator.page(pindex)
    page_list = get_page_list(total_page, pindex)

    context = {
        'title': '商品列表',
        'page': page,
        'category_list': category_list,
        'category_now': category_now,
        'new_list': new_list,
        'order': order,
        'page_list': page_list,

    }

    context['total_count']=get_cart_total(request)

    return render(request, 'list.html', context)


def detail(request, sku_id):
    try:
        sku = GoodsSKU.objects.get(pk=sku_id)
    except:
        raise Http404()

    category_list = GoodsCategory.objects.all()

    new_list = sku.category.goodssku_set.all().order_by('-id')[0:2]

    other_list = sku.goods.goodssku_set.all()
    if request.user.is_authenticated():
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
    context['total_count']=get_cart_total(request)

    return render(request, 'detail.html', context)

class MySearchView(SearchView):
    def get(self, request, *args, **kwargs):
        self.cart_request=request
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title']='搜索结果'
        context['category_list']=GoodsCategory.objects.all()

        #页码控制
        total_page=context['paginator'].num_pages
        pindex=context['page_obj'].number
        context['page_list']=get_page_list(total_page,pindex)
        context['total_count'] = get_cart_total(self.cart_request)

        return context


def get_cart_total(request):
    '''获取购物车中商品的总数量'''
    total_count = 0
    # 判断用户是否登录
    if request.user.is_authenticated():
        # 如果登录则从redis中读取
        redis_client = get_redis_connection()
        for v in redis_client.hvals('cart%d' % request.user.id):
            # total_count += int(v)
            total_count += 1
    else:
        # 如果未登录则从cookie中读取
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            cart_dict = json.loads(cart_str)
            for k, v in cart_dict.items():
                total_count += v

    return total_count