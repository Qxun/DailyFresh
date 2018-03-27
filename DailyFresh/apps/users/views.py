<<<<<<< HEAD
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View
import re
from .models import User
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from django.contrib.auth import authenticate, login, logout


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
        response = redirect('/users/info')

        if remember is None:
            response.delete_cookie('uname')
        else:
            response.set_cookie('uname', uname, expires=60 * 60 * 24 * 7)

        return response


def logout_user(request):
    logout(request)
    return redirect('/users/login')


def info(request):
    context = {
        'title': '个人信息'
    }

    return render(request, 'user_center_info.html', context)

def order(request):
    context = {
        'title': '个人信息'
    }
    return render(request, 'user_center_order.html', context)


class SiteView(View):
    def get(self, request):
        context = {}
        return render(request, 'user_center_site.html', context)

    def post(self, request):
        context = {}
        pass


=======
from django.shortcuts import render

# Create your views here.
>>>>>>> 665b20e7f457edc4d588b7fe3b5281f4e73363e5
