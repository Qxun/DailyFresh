import json

from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View
import re
from django_redis import get_redis_connection
from goods.models import GoodsSKU
from .models import User, Address, AreaInfo
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from utils.views import LoginRequiredViewMixin


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html', {'title': '注册'})

    def post(self, request):
        dict = request.POST
        # print(dict)
        uname = dict.get('user_name')
        pwd = dict.get('pwd')
        cpwd = dict.get('cpwd')
        email = dict.get('email')
        allow = dict.get('allow')
        context = {
            'uname': uname,
            'pwd': pwd,
            'cpwd': cpwd,
            'email': email,
            'err_msg': '',
            'title': '注册处理'
        }
        if allow is None:
            context['err_msg'] = '请接收协议'
            return render(request, 'register.html', context)
        # print(1)
        if not all([uname, pwd, cpwd, email]):
            context['err_msg'] = '请输入完整信息'
            return render(request, 'register.html', context)
        # print(2)
        if pwd != cpwd:
            context['err_msg'] = '两次密码不相同'
            return render(request, 'register.html', context)
        # print(3)
        if User.objects.filter(username=uname).count() > 0:
            context['err_msg'] = '用户名已存在'
            return render(request, 'register.html', context)
        # print(4)
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            context['err_msg'] = '邮箱格式不正确'
            return render(request, 'register.html', context)
        # print(5)
        if User.objects.filter(email=email).count() > 0:
            context['err_msg'] = '邮箱已经被注册'
            return render(request, 'register.html', context)
        # print(6)

        user = User.objects.create_user(uname, email, pwd)
        print(user)
        user.is_active = False
        user.save()

        # 发送邮件
        # 加密
        serializer = Serializer(settings.SECRET_KEY, 60 * 60)
        value = serializer.dumps({'id': user.id}).decode('utf-8')
        msg = '<a href="http://127.0.0.1:8000/users/active/%s">点击激活</a>' % value
        send_mail('天天生鲜用户激活', '', settings.EMAIL_FROM, [email], html_message=msg)

        return HttpResponse('注册成功，请稍候到邮箱中激活账户')


def active(request, value):
    try:
        serializer = Serializer(settings.SECRET_KEY)
        dict = serializer.loads(value)
    except SignatureExpired as e:
        return HttpResponse("连接已过期")
    id = dict.get('id')
    user = User.objects.get(pk=id)
    user.is_active = True
    user.save()
    return redirect('/users/login')


def exists(request):
    name = request.GET.get('uname')

    if name is not None:
        result = User.objects.filter(username=name).count()

    return JsonResponse({'result': result})


class LoginView(View):
    def get(self, request):
        uname = request.COOKIES.get('uname', '')
        context = {
            'title': '登陆',
            'uname': uname,
        }
        return render(request, 'login.html', context)

    def post(self, request):
        value = request.POST
        uname = value.get('username')
        pwd = value.get('pwd')
        remember = value.get('remember')

        context = {
            'uname': uname,
            'pwd': pwd,
            'err_msg': '',
            'title': '登陆处理'
        }

        if not all([uname, pwd]):
            context['err_msg'] = '请输入完整的信息'
            return render(request, 'login.html', context)

        user = authenticate(username=uname, password=pwd)

        if user is None:
            context['err_msg'] = '用户名或密码错误'
            return render(request, 'login.html', context)

        if not user.is_active:
            context['err_msg'] = '请激活'
            return render(request, 'login.html', context)

        # 状态保持
        login(request, user)

        next_url = request.GET.get('next', '/users/info')
        response = redirect(next_url)

        if remember is None:
            response.delete_cookie('uname')
        else:
            response.set_cookie('uname', uname, expires=60 * 60 * 24 * 7)

        # 将cookies中的购物车信息转存入redis中
        # 在redis中存储的结构为：商品编号是属性，数量是属性值
        # 1.读取cookie中的购物车信息，转成字典
        cart_str = request.COOKIES.get('cart')
        if cart_str:
            key = 'cart%d' % request.user.id
            redis_client = get_redis_connection()
            cart_dict = json.loads(cart_str)
            # 2.遍历字典
            for k, v in cart_dict.items():
                # 3.判断redis中是否已经存在这个商品
                if redis_client.hexists(key, k):
                    # 3.1如果有则数量相加
                    count1 = int(redis_client.hget(key, k))
                    count2 = v
                    count0 = count1 + count2
                    if count0 > 5:
                        count0 = 5
                    redis_client.hset(key, k, count0)
                else:
                    # 3.2如果无则添加
                    redis_client.hset(key, k, v)
            # 已经成功转存到redis，删除cookie中的信息
            response.delete_cookie('cart')

        return response


def logout_user(request):
    logout(request)
    return redirect('/users/login')


@login_required
def info(request):
    address = request.user.address_set.filter(isDefault=True)
    if address:
        address = address[0]
    else:
        address = None

    redis_client = get_redis_connection()
    gid_list = redis_client.lrange('history%d' % request.user.id, 0, -1)
    good_list = []
    for gid in gid_list:
        good_list.append(GoodsSKU.objects.get(pk=gid))

    context = {
        'title': '个人信息',
        'address': address,
        'goods_list': good_list
    }

    return render(request, 'user_center_info.html', context)


@login_required
def order(request):
    context = {
        'title': '个人信息'
    }
    return render(request, 'user_center_order.html', context)


class SiteView(LoginRequiredViewMixin, View):
    def get(self, request):
        addr_list = Address.objects.filter(user=request.user)

        context = {
            'title': '收货地址',
            'add_list': addr_list,
        }
        return render(request, 'user_center_site.html', context)

    def post(self, request):
        udict = request.POST
        uname = udict.get('uname')
        provice = udict.get('provice')
        city = udict.get('city')
        district = udict.get('district')
        addr = udict.get('addr')
        code = udict.get('code')
        phone = udict.get('phone')
        default = udict.get('default')
        # context = {
        #     'uname':uname,
        #     'provice':provice,
        #     'city':city,
        #     'district':district,
        #     'addr':addr,
        #     'code':code,
        #     "phone":phone,
        #     'title':''
        # }
        if not all([uname, provice, city, district, addr, code, phone]):
            return render(request, 'user_center_site.html', {'err_msg': '信息填写不完整'})

        address = Address()
        address.receiver_name = uname
        address.province_id = provice
        address.city_id = city
        address.district_id = district
        address.detail_addr = addr
        address.zip_code = code
        address.receiver_mobile = phone
        if default:
            address.isDefault = True
        address.user = request.user
        address.save()

        return redirect('/users/site')


def area(request):
    pid = request.GET.get('pid')
    if pid is None:
        # 查询所有省信息
        slist = AreaInfo.objects.filter(aParent__isnull=True)
    else:
        slist = AreaInfo.objects.filter(aParent_id=pid)
    slist2 = []
    for s in slist:
        slist2.append({'id':s.id,'title':s.title})
    return JsonResponse({'list': slist2})