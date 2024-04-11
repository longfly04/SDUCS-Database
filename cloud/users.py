# 登录模块

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from django.conf import settings

from .models import *
from .form import *

# 获取User模型
User = get_user_model()


# # 生成随机账号
# import random

# def random_user():
#     usableName_char = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
#     usablePassword_char = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
#     # 生成8位账号和12位密码
#     userName = ''.join([random.choice(usableName_char) for _ in range(8)])         
#     userPassWord = ''.join([random.choice(usablePassword_char) for _ in range(12)])
    
#     # 生成12位邮箱
#     email_char = '1234567890abcdefghijklmnopqrstuvwxyz'
#     com_char = ['gmail.com', 'sdu.edu.cn', 'qq.com', '163.com']
#     email = ''.join([random.choice(email_char) + '@' + random.choice(com_char) for _ in range(12)])    
#     print('create user: name\t' + userName + '\tpassword\t' + userPassWord + '\temail\t' + email)
    
#     return userName, userPassWord, email


# 初始界面
def site(request):
    if request.method == 'GET':
        return render(request, 'welcome.html')


# 注册
def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')

    form = RegisterForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        email = form.cleaned_data['email']
        # 已经存在同名的用户，注册失败
        username_exists = User.objects.filter(userName = username).exists()
        if username_exists:
            context = {'code': 400, 'message': '您输入的用户名已存在！', 'next_url': '/user/register'}
        else:
            # 已经存在相同的邮箱，注册失败
            email_exists = User.objects.filter(userEmail = email).exists()
            if email_exists:
                context = {'code': 400, 'message': '您输入的邮箱已存在！', 'next_url': '/user/register'}
            else:
                # 注册成功，创建用户
                User.objects.create_user(username = username, password = password, email = email)
                user = User.objects.get(userName = username)
                useraddress = form.cleaned_data['useraddress']
                userpicture = request.FILES.get('file', None)
                if useraddress:
                    user.userAddress = useraddress
                    user.save()
                if userpicture:
                    file_name = 'picture/{user}.{name}'.format(user = username, name = userpicture.name.split(".")[-1])
                    full_name = '{root}/{filename}'.format(root = settings.MEDIA_ROOT, filename = file_name)
                    with open(full_name, 'wb+') as f:       # 将头像存储到项目中
                        for chunk in userpicture.chunks():
                            f.write(chunk)
                    user.userPicture = file_name
                    user.save()
                context = {'code': 200, 'message': '注册成功喵！VCloud期待您的到来！', 'next_url': '/user/login'}
    else:
        # 格式错误产生error
        context = {'code': 400, 'message': '用户名或密码格式错误！', 'next_url': '/user/register'}
    
    # 页面跳转
    return render(request, 'pagejump.html', context)



# 登录
def signin(request):
    # 登陆跳转实现
    # 参考：https://www.cnblogs.com/jack-233/p/11428254.html
    if request.method == 'GET':
        next_url = request.GET.get("next", '')
        return render(request, 'login.html', { 'next_url': next_url })

    form = LoginForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        # remember = int(request.POST.get('remember'))
        remember = request.POST.get('remember')
        next_url = request.POST.get('next_url')
        # 使用authenticate进行登录验证，验证成功会返回一个user对象，失败则返回None
        user = authenticate(request, username = username, password = password)
        
        # 注意：如果is_active为False，authenticate将会返回None，导致无法判断激活状态。解决方法是在seetings中配置后端认证列表：
        # AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.AllowAllUsersModelBackend']
        
        if user and user.is_active:                                         # 验证成功且用户已激活
            # 将登陆的信息封装到request.user,包括session
            login(request,user)
            request.session['username'] = username
            if remember:            # 设置session过期时间，None表示使用系统默认的过期时间
                request.session.set_expiry(None)
            else:                   # 0代表关闭浏览器session失效
                request.session.set_expiry(0)
            # 跳转登录
            if not next_url:
                next_url = '/user/index'
            context = {'code': 200, 'message': '验证通过！', 'next_url': next_url}
        elif user and not user.is_active:                                   # 用户验证成功但未激活
            context = {'code': 400, 'message': '用户未激活！', 'next_url': '/user/login'}
        else:                                                               # 验证失败
            context = {'code': 400, 'message': '用户名或密码错误！', 'next_url': '/user/login'}
    else:
        # 格式错误产生error
        context = {'code': 400, 'message': '用户名或密码格式错误！', 'next_url': '/user/login'}
    # 页面跳转
    return render(request, 'pagejump.html', context)


# 退出
@login_required
def exit(request):
    # 清除当前用户的session信息
    auth.logout(request)
    context = {'code': 200, 'message': '再见喵~VCloud一直在这里等你~', 'next_url': '/user/login'}
    return render(request, 'pagejump.html', context)



# 用户界面
@login_required
def index(request, username = None):
    # 访问自己的界面，能够访问地址
    if not username or username == request.user.userName:
        user = User.objects.get(userName = request.user.userName)
        username = user.userName
        useremail = user.userEmail
        useraddress = user.userAddress
        userpicture = user.userPicture
        if userpicture:
            userpicture = 'media/' + str(userpicture)
        else:
            userpicture = 'static/images/picture.jpeg'
        # 展示代码库
        repo = []
        for ur in UserRepository.objects.filter(uID = user.userID):
            r = ur.rID
            repo.append([r.rName, r.rIntro, r.rState])
        context = {'code': 200, 'isself': 'true', 'name': username, 'email': useremail, 'address': useraddress, 'picture': userpicture, 'repo': repo}
    # 访问他人的界面，不能够访问地址
    else:
        try:
            user = User.objects.get(userName = username)
            username = user.userName
            useremail = user.userEmail
            userpicture = user.userPicture
            if userpicture:
                userpicture = 'media/' + str(userpicture)
            else:
                userpicture = 'static/images/picture.jpeg'
            # 展示代码库
            repo = []
            for ur in UserRepository.objects.filter(uID = user.userID):
                r = ur.rID
                repo.append([r.rName, r.rIntro, r.rState])
            context = {'code': 200, 'isself': 'false', 'name': username, 'email': useremail, 'picture': userpicture, 'repo': repo}
        except:
            context = {'code': 400, 'message': '您搜索的用户不存在！', 'next_url': '/user/index'}
            return render(request, 'pagejump.html', context)
    # 跳转界面
    return render(request, 'index.html', context)
