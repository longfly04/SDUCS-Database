# 问题管理模块

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from .models import *
from .form import *

import json

# 创建问题
@login_required
def create_issue(request, repo):
    if request.method == 'GET':
        return render(request, 'createissue.html')

    form = CreateIssue(request.POST)
    if form.is_valid():
        topic = form.cleaned_data['topic']
        # 检查是否存在仓库
        try:
            repository = Repository.objects.get(rName = repo)
        except:
            context = {'code': 400, 'message': '所检索的仓库不存在！', 'next_url': '/repository/searchrepo'}
            return render(request, 'pagejump.html', context)
        # 已经存在同名的问题，新建失败
        topic_exists = Issue_UR.objects.filter(iTopic = topic).exists()
        if topic_exists:
            context = {'code': 400, 'message': '新建问题失败！已存在同名问题！', 'next_url': '/repository/{repo}/createissue'.format(repo = repo)}
        else:
            # 创建问题成功，将所有空格替换为下划线
            topic = topic.strip().replace(' ', '_')
            Issue_UR.objects.create(iTopic = topic, uID = User.objects.get(userID = request.user.userID), rID = repository)
            context = {'code': 200, 'message': '新建问题成功！', 'next_url': '/repository/{repo}/viewissue/{issue}'.format(repo = repo, issue = topic)}
    else:
        context = {'code': 400, 'message': '新建问题失败！填写信息格式不正确！', 'next_url': '/repository/{repo}/createissue'.format(repo = repo)}
    
    return render(request, 'pagejump.html', context)


# 列出问题
@login_required
def list_issue(request, repo):
    # 检查是否存在仓库
    try:
        repository = Repository.objects.get(rName = repo)
    except:
        context = {'code': 400, 'message': '所检索的仓库不存在！', 'next_url': '/repository/searchrepo'}
        return render(request, 'pagejump.html', context)
    issues = Issue_UR.objects.filter(rID = repository)
    issues = [[i.uID.userName, 'media/' + str(i.uID.userPicture), i.iTopic, i.iState, i.itime] for i in issues]
    context = {'code': 200, 'message': '查询成功！', 'issues': issues, 'repo': repo}
    return render(request, 'listissue.html', context)


# 查看问题
@login_required
def view_issue(request, repo, topic):
    # 检查是否存在仓库
    try:
        repository = Repository.objects.get(rName = repo)
    except:
        context = {'code': 400, 'message': '所检索的仓库不存在！', 'next_url': '/repository/searchrepo'}
        return render(request, 'pagejump.html', context)
    # 检查是否存在问题
    try:
        issue_ur = Issue_UR.objects.get(rID = repository, iTopic = topic)
    except:
        context = {'code': 400, 'message': '所检索的问题不存在！', 'next_url': '/repository/{repo}/viewissue'.format(repo = repo)}
        return render(request, 'pagejump.html', context)
    # 按照时间顺序从旧到新列出所有帖子，每个帖子以100字符为一行
    issues = Issues.objects.filter(iID = issue_ur)
    if issues:
        issues = sorted([[i.iuid.userName, 'media/' + str(i.iuid.userPicture), 
                [i.article[100 * line: min(100 * (line + 1), len(i.article))] for line in range(len(i.article) // 100 + 1)], i.time] for i in issues], key = lambda x: x[-1])
    if issue_ur.iState:
        state = 'OPEN'
    else:
        state = 'CLOSE'
    is_contributor = UserRepository.objects.filter(uID = request.user.userID, rID = repository).exists()
    context = {'code': 200, 'message': '查询成功！', 'issues': issues, 'topic': topic, 'state': state, 'is_contributor': is_contributor, 'repo': repo}
    return render(request, 'viewissue.html', context)


# 新增问题帖子
@login_required
def add_issue_topic(request, repo, topic):
    if request.method == 'GET':
        return render(request, 'addissue.html')

    form = AddIssueTopic(request.POST)
    if form.is_valid():
        article = form.cleaned_data['article']
        if article:
            # 检查是否存在仓库
            try:
                repository = Repository.objects.get(rName = repo)
            except:
                context = {'code': 400, 'message': '所检索的仓库不存在！', 'next_url': '/repository/searchrepo'}
                return render(request, 'pagejump.html', context)    
            # 检查是否存在问题
            try:
                issue_ur = Issue_UR.objects.get(rID = repository, iTopic = topic)
            except:
                context = {'code': 400, 'message': '所检索的问题不存在！', 'next_url': '/repository/{repo}/viewissue'.format(repo = repo)}
                return render(request, 'pagejump.html', context)
            # 检查问题是否开放
            if not issue_ur.iState:
                context = {'code': 200, 'message': '该问题已关闭，无法回帖！', 'next_url': '/repository/{repo}/viewissue/{topic}'.format(repo = repo, topic = topic)}
                return render(request, 'pagejump.html', context)  
            # 新增问题帖子
            Issues.objects.create(article = article, iuid = User.objects.get(userID = request.user.userID), iID = issue_ur)
            context = {'code': 200, 'message': '新建问题帖子成功！', 'next_url': '/repository/{repo}/viewissue/{topic}'.format(repo = repo, topic = topic)}
        else:
            context = {'code': 400, 'message': '新建问题帖子失败！帖子内容不能为空！', 'next_url': 'repository/{repo}/viewissue/{topic}/addtopic'.format(repo = repo, topic = topic)}
    else:
        context = {'code': 400, 'message': '新建问题帖子失败！填写信息格式不正确！', 'next_url': 'repository/{repo}/viewissue/{topic}/addtopic'.format(repo = repo, topic = topic)}

    return render(request, 'pagejump.html', context)  


# 更改问题开放状态
# 修改仓库状态
@login_required
def change_issue_state(request, repo, topic):
    try:
        data = json.loads(request.body)
        state = data['state']
        issue_ur = Issue_UR.objects.get(rID = Repository.objects.get(rName = repo), iTopic = topic)
        if state == 'OPEN':
            issue_ur.iState = True
            issue_ur.save()
        else:
            issue_ur.iState = False
            issue_ur.save()
        return render(request, 'viewissue.html')
    except:
        return render(request, 'pagejump.html', context = {'code': 400, 'message': '无效的状态修改！', 'next_url': '/repository/{repo}/view'.format(repo = repo)})

