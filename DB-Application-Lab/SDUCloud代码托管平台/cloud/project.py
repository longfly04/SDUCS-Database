# 计划管理模块

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from .models import *
from .form import *

import time
import datetime

# 以时间轴形式展示计划
@login_required
def view_project(request, repo):
    if request.method == 'GET':
        # 检查是否存在仓库
        try:
            repository = Repository.objects.get(rName = repo)
        except:
            context = {'code': 400, 'message': '所检索的仓库不存在！', 'next_url': '/repository/searchrepo'}
            return render(request, 'pagejump.html', context)
        # 查找所有计划，只显示在今天之后的
        today = time.strftime('%d/%m/%Y', time.localtime())
        strtoday = time.strftime('%B %d %Y, %A', time.localtime())
        projects = sorted([{'topic': p.projTopic, 'time': p.time.strftime('%d/%m/%Y'), 'strtime': p.time.strftime('%B %d %Y, %A'), 'article': p.article, 'realtime': p.time.strftime('%Y%m%d')} 
                            for p in Projects.objects.filter(rID = repository) if p.time.strftime('%Y%m%d') >= time.strftime('%Y%m%d', time.localtime())
                        ], key = lambda x: x['realtime'])
        context = {'code': 200, 'message': '检索成功！', 'projects': projects, 'today': today, 'strtoday': strtoday}
        return render(request, 'timeline.html', context)


# 新建计划
@login_required
def create_project(request, repo):
    if request.method == 'GET':
        return render(request, 'createtimeline.html')
    
    form = CreateProject(request.POST)
    if form.is_valid():
        try:
            repository = Repository.objects.get(rName = repo)
        except:
            context = {'code': 400, 'message': '所检索的仓库不存在！', 'next_url': '/repository/searchrepo'}
            return render(request, 'pagejump.html', context)
        projTopic = form.cleaned_data['projTopic']
        article = form.cleaned_data['article']
        time = form.cleaned_data['time']
        if projTopic and article and time:
            Projects.objects.create(projTopic = projTopic, article = article, time = time, rID = repository)
            context = {'code': 200, 'message': '创建问题成功！', 'next_url': '/repository/{repo}/project/viewproject'.format(repo = repo)}
        else:
            context = {'code': 400, 'message': '创建问题失败！信息填写不完整！', 'next_url': '/repository/{repo}/project/createproject'.format(repo = repo)}
    else:
        context = {'code': 400, 'message': '信息填写格式错误！', 'next_url': '/repository/{repo}/project/createproject'.format(repo = repo)}
    return render(request, 'pagejump.html', context)