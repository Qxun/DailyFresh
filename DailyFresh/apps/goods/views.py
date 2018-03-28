from django.shortcuts import render
from .models import Goods, GoodsCategory, IndexGoodsBanner, IndexPromotionBanner, IndexCategoryGoodsBanner


# Create your views here.

def index(request):
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

    return render(request, 'index.html', context)


def list(request):
    return render(request, 'list.html')


def detail(request):
    return render(request, 'detail.html')
