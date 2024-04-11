# 仓库管理模块

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.conf import settings

from .models import *
from .form import *

import os
import json

# 建库
@login_required
def create_repo(request):
    if request.method == 'GET':
        return render(request, 'createrepo.html')

    form = CreateRepo(request.POST)
    if form.is_valid():
        reponame = form.cleaned_data['reponame']
        state = form.cleaned_data['state']
        intro = form.cleaned_data['intro']
        # 已经存在同名的仓库，建库失败
        reponame_exists = Repository.objects.filter(rName = reponame).exists()
        if reponame_exists:
            context = {'code': 400, 'message': '建库失败！已存在同名仓库！', 'next_url': '/repository/createrepo'}
        else:
            # 建库成功，创建仓库，创建路径，并添加初始贡献者
            if state == '0':
                state = False
            else:
                state = True
            Repository.objects.create(rName = reponame, rState = state)
            if intro:
                repo = Repository.objects.get(rName = reponame)
                repo.rIntro = intro
                repo.save()
            UserRepository.objects.create(rID = Repository.objects.get(rName = reponame), uID = User.objects.get(userID = request.user.userID))
            if not os.path.exists(settings.MEDIA_ROOT + '/repository/' + reponame):
                os.makedirs(settings.MEDIA_ROOT + '/repository/' + reponame)
            context = {'code': 200, 'message': '建库成功！', 'next_url': '/repository/{repo}/view'.format(repo = reponame)}
    else:
        context = {'code': 400, 'message': '建库失败！填写信息格式不正确！', 'next_url': '/repository/createrepo'}
    
    return render(request, 'pagejump.html', context)



# 搜索仓库，列出所有前缀匹配的公开仓库以及作为贡献者的私有仓库
@login_required
def search_repo(request):
    if request.method == 'GET':
        return render(request, 'searchrepo.html')
    
    form = SearchRepo(request.POST)
    if form.is_valid():
        reponame = form.cleaned_data['reponame']
        user = User.objects.get(userName = request.user.userName)
        findrepos = Repository.objects.filter(rName__startswith = reponame)
        repos = []
        for r in findrepos:
            if not (r.rState != 1 and (not UserRepository.objects.filter(uID = user.userID, rID = r))):
                repos.append([r.rName, r.rIntro])
        if repos:
            context = {'code': 200, 'message': '', 'repos': repos}
        else:
            context = {'code': 400, 'message': '搜索失败！不存在所寻找的仓库！', 'repos': None}
        return render(request, 'searchrepo.html', context)
    else:
        context = {'code': 400, 'message': '搜索失败！填写信息格式不正确！', 'next_url': '/repository/searchrepo'}
        return render(request, 'pagejump.html', context)



# 查看仓库
@login_required
def view_repo(request, repo, path = None):
    if request.method == 'GET':
        # 检查是否存在仓库
        try:
            repository = Repository.objects.get(rName = repo)
        except:
            context = {'code': 400, 'message': '所检索的仓库不存在！', 'next_url': '/repository/searchrepo'}
            return render(request, 'pagejump.html', context)
        # 检查路径是否存在
        if path:
            folderpath = 'repository/' + repo + '/' + path
            fullpath = settings.MEDIA_ROOT + '/repository/' + repo + '/' + path
        else:
            folderpath = 'repository/' + repo
            fullpath = settings.MEDIA_ROOT + '/repository/' + repo
        if not os.path.exists(fullpath):
            context = {'code': 400, 'message': '所检索的路径不存在！', 'next_url': '/repository/{repo}/view'.format(repo = repo)}
            return render(request, 'pagejump.html', context)
        # 检验是否为贡献者
        user = User.objects.get(userName = request.user.userName)
        is_contributor = UserRepository.objects.filter(uID = user, rID = repository).exists()
        # 作为贡献者，能够访问仓库及修改；公开仓库能够被所有人访问；私有仓库只能被贡献者访问
        if (not repository.rState) and (not is_contributor):
            context = {'code': 400, 'message': '仓库非公开！', 'next_url': '/repository/searchrepo'}
            return render(request, 'pagejump.html', context)
        
        # 整理文档，分为文件夹和文件整理，注意文件名在磁盘中也是以文件夹储存的
        for findpath, findfolders, findfiles in os.walk(fullpath):
            break
        folders = []
        files = []
        for folder in findfolders:
            # 如果本身就是文件，加入files中；如果不是文件，就一定是文件夹（有可能是空文件夹）
            if VCFiles.objects.filter(file__startswith = folderpath + '/' + folder).exists():
                for sonfindpath, sonfindfolders, sonfindfiles in os.walk(fullpath + '/' + folder):
                    break
                if not sonfindfolders:
                    files.append(folder)
                else:
                    folders.append(folder)
        if path:
            path = repo + '/' + path
            lastpath = path[: path.rfind('/')]
        else:
            path = repo
            lastpath = ''
        r = Repository.objects.get(rName = repo)
        contributor = [ur.uID for ur in UserRepository.objects.filter(rID = r)]
        if r.rState == True:
            state = 'PUBLIC'
        else:
            state = 'PRIVATE'
        context = {
            'code': 200, 'message': '访问成功！', 'path': path, 'folders': folders, 'files': files, 
            'lastpath': lastpath, 'repo': repo, 'contributor': contributor, 'is_contributor': is_contributor,
            'state': state 
        }
        return render(request, 'repository.html', context)


# 查看文本文件
# 参考：https://blog.csdn.net/chuck_robert/article/details/118467038?spm=1001.2014.3001.5501
# 目前支持语言：C/C++，Python，CSS，Java，JS, markdown
# 文本后缀名支持：.c .cpp .py .python .java .css .js .md
@login_required
def open_file(request, repo, path = None):
    if request.method == 'GET':
        # 检查是否存在仓库
        try:
            repository = Repository.objects.get(rName = repo)
        except:
            context = {'code': 400, 'message': '所检索的仓库不存在！', 'next_url': '/repository/searchrepo'}
            return render(request, 'pagejump.html', context)
        # 检查路径是否存在
        if path:
            filepath = 'repository/' + repo + '/' + path
            fullpath = settings.MEDIA_ROOT + '/repository/' + repo + '/' + path
        else:
            filepath = 'repository/' + repo
            fullpath = settings.MEDIA_ROOT + '/repository/' + repo
        if not os.path.exists(fullpath):
            context = {'code': 400, 'message': '所检索的路径不存在！', 'next_url': '/repository/{repo}/view'.format(repo = repo)}
            return render(request, 'pagejump.html', context)
        # 检验是否为贡献者
        user = User.objects.get(userName = request.user.userName)
        is_contributor = UserRepository.objects.filter(uID = user, rID = repository).exists()
        # 私有仓库不能被非贡献者访问
        if (not repository.rState) and (not is_contributor):
            context = {'code': 400, 'message': '仓库非公开！', 'next_url': '/repository/searchrepo'}
            return render(request, 'pagejump.html', context)
        
        # 检查是否为文件以及是否为支持打开的文本文件
        if len(VCFiles.objects.filter(file__startswith = filepath)) != 1:
            context = {'code': 400, 'message': '打开的不是文件！', 'next_url': '/repository/{repo}/view'.format(repo = repo)}
            return render(request, 'pagejump.html', context)
        vcfile = VCFiles.objects.get(file__startswith = filepath)
        # 分析语言类型
        language = str(vcfile.file).split(".")[-1]
        if language in ['txt', 'c', 'cpp', 'py', 'python', 'java', 'css', 'js', 'md']:
            if language == 'py':
                language = 'python'
            elif language == 'css':
                language = 'CSS'
            elif language == 'js':
                language = 'JS'
            elif language == 'md':
                language = 'markdown'
        else:
            # context = {'code': 400, 'message': '打开的是不支持的文件！', 'next_url': '/repository/{repo}/view'.format(repo = repo)}
            # return render(request, 'pagejump.html', context)
            context = {'code': 200, 'message': '打开文本失败！', 'file': None, 'language': None, 'filename': str(vcfile.file).split("/")[-2]}
            return render(request, 'openfile.html', context)
        # 按行传入代码，注意转换特殊字符
        file = [] 
        with open(settings.MEDIA_ROOT + '/' + str(vcfile.file), encoding='UTF-8') as f:
            for line in f.readlines():
                # line = line.replace('&', '&#38')
                # line = line.replace('"', '&#34').replace('<', '&#60').replace('>', '&#62').replace(' ', '&#160')
                file.append(line)
        context = {'code': 200, 'message': '打开文本成功！', 'file': file, 'language': language, 'filename': str(vcfile.file).split("/")[-2]}
        return render(request, 'openfile.html', context)



# 修改仓库状态
@login_required
def change_state(request, repo):
    try:
        data = json.loads(request.body)
        state = data['state']
        r = Repository.objects.get(rName = repo)
        if state == 'PUBLIC':
            r.rState = True
            r.save()
        else:
            r.rState = False
            r.save()
        return render(request, 'repository.html')
    except:
        return render(request, 'pagejump.html', context = {'code': 400, 'message': '无效的状态修改！', 'next_url': '/repository/searchrepo'})


# 增加贡献者
def add_contributor(request, repo):
    if request.method == 'GET':
        return render(request, 'addcontributor.html')

    # 检查仓库是否存在以及用户是否为仓库贡献者
    try:
        ur = UserRepository.objects.get(uID = request.user.userID, rID = Repository.objects.get(rName = repo))
    except:
        context = {'code': 400, 'message': '增加贡献者失败！没有找到仓库或没有修改权限！', 'next_url': '/repository/{repo}/view'.format(repo = repo)}
        return render(request, 'pagejump.html', context)
    
    form = AddContributor(request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        # 如果不存在相应的贡献者关系，添加
        if User.objects.filter(userName = username).exists() and \
            not UserRepository.objects.filter(uID = User.objects.get(userName = username), rID = Repository.objects.get(rName = repo)).exists():
            UserRepository.objects.create(uID = User.objects.get(userName = username), rID = Repository.objects.get(rName = repo))
            context = {'code': 200, 'message': '增加贡献者成功！', 'next_url': '/repository/{repo}/view'.format(repo = repo)}
        else:
            context = {'code': 400, 'message': '增加贡献者失败！已存在该贡献者或不存在该用户！', 'next_url': '/repository/{repo}/addcontributor'.format(repo = repo)}

    else:
        context = {'code': 400, 'message': '增加贡献者失败！填写信息格式不正确！', 'next_url': '/repository/{repo}/addcontributor'.format(repo = repo)}
    
    return render(request, 'pagejump.html', context)


# 基于Myers SES(最短编辑脚本)动态规划算法的diff方法
# 参考：https://www.dazhuanlan.com/provista/topics/1118636
def diff(path1, path2):
    '''
        用于逐行比较文档差异，传入文件路径作为参数，返回一个数组，表征修改过程，修改忽略行末空格的不同.
        其中，path1为当前文件，path2为旧文件

        -   删除原文件某行
        +   添加新文件中的某行
        .   原文件和新文件该行相同（换为空格）

        例如:
        -   a = 10
        +   a = 100
        .   
        -   def diff():
        +   def myers_diff():
        .       pass

    '''
    with open(path1, encoding = 'UTF-8') as f1, open(path2, encoding = 'UTF-8') as f2:
        file1, file2 = [l.rstrip() for l in f1.readlines()], [l.rstrip() for l in f2.readlines()]
        
        # 路径长度动态规划数组dp，父节点数组fa
        n, m = len(file1), len(file2)
        dp = [[0 for j in range(m + 1)] for i in range(n + 1)] 
        fa = [[None for j in range(m + 1)] for i in range(n + 1)] 
        # 动态规划，时间复杂度为 O(mn)，优先级：向右下不变，向下删除，向右增加
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if file1[i - 1] == file2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                    fa[i][j] = (i - 1, j - 1)
                elif dp[i - 1][j] <= dp[i][j - 1]:
                    dp[i][j] = dp[i - 1][j] + 1
                    fa[i][j] = (i - 1, j)
                else:
                    dp[i][j] = dp[i][j - 1] + 1
                    fa[i][j] = (i, j - 1)
        # 回溯得到路径
        process = []
        i, j = (n, m)
        while fa[i][j] != None:
            fi, fj = fa[i][j]
            if (i, j) == (fi + 1, fj + 1):
                # process.append(['.', file1[fi] + '\n'])
                process.append([' ', file1[fi] + '\n'])
            elif (i, j) == (fi + 1, fj):
                process.append(['-', file1[fi] + '\n'])
            elif (i, j) == (fi, fj + 1):
                process.append(['+', file2[fj] + '\n'])
            i, j = fi, fj
        while i != 0:
            process.append(['-', file1[i - 1] + '\n'])
            i -= 1
        while j != 0:
            process.append(['+', file2[j - 1] + '\n'])
            j -= 1
        
        # return list(reversed(process))
        return list(reversed([op + '\t' + line for op, line in process]))


# 查看历史文本文件并比较异同
# 目前支持语言：C/C++，Python，CSS，Java，JS, markdown
# 文本后缀名支持：.c .cpp .py .python .java .css .js .md
@login_required
def diff_file(request, repo, path = None):
    if request.method == 'GET':
        # 检查是否存在仓库
        try:
            repository = Repository.objects.get(rName = repo)
        except:
            context = {'code': 400, 'message': '所检索的仓库不存在！', 'next_url': '/repository/searchrepo'}
            return render(request, 'pagejump.html', context)
        # 检查路径是否存在
        if path:
            filepath = 'repository/' + repo + '/' + path
            fullpath = settings.MEDIA_ROOT + '/repository/' + repo + '/' + path
        else:
            filepath = 'repository/' + repo
            fullpath = settings.MEDIA_ROOT + '/repository/' + repo
        if not os.path.exists(fullpath):
            context = {'code': 400, 'message': '所检索的路径不存在！', 'next_url': '/repository/{repo}/view'.format(repo = repo)}
            return render(request, 'pagejump.html', context)
        # 检验是否为贡献者
        user = User.objects.get(userName = request.user.userName)
        is_contributor = UserRepository.objects.filter(uID = user, rID = repository).exists()
        # 私有仓库不能被非贡献者访问
        if (not repository.rState) and (not is_contributor):
            context = {'code': 400, 'message': '仓库非公开！', 'next_url': '/repository/searchrepo'}
            return render(request, 'pagejump.html', context)
        
        # 检查是否为文件以及是否为支持打开的文本文件
        if len(VCFiles.objects.filter(file__startswith = filepath)) != 1:
            context = {'code': 400, 'message': '打开的不是文件！', 'next_url': '/repository/{repo}/view'.format(repo = repo)}
            return render(request, 'pagejump.html', context)
        vcfile = VCFiles.objects.get(file__startswith = filepath)
        # 分析语言类型
        language = str(vcfile.file).split(".")[-1]
        if language in ['txt', 'c', 'cpp', 'py', 'python', 'java', 'css', 'js', 'md']:
            if language == 'py':
                language = 'python'
            elif language == 'css':
                language = 'CSS'
            elif language == 'js':
                language = 'JS'
            elif language == 'md':
                language = 'markdown'
        else:
            # context = {'code': 400, 'message': '打开的是不支持的文件！', 'next_url': '/repository/{repo}/view'.format(repo = repo)}
            # return render(request, 'pagejump.html', context)
            context = {'code': 200, 'message': '打开文本失败！', 'file': None, 'language': None, 'filename': str(vcfile.file).split("/")[-2]}
            return render(request, 'openfile.html', context)
        
        # 查找所有的历史文件，按照从新到旧的顺序给出，并与上一次的文件比较异同
        # 当前文件
        file = [] 
        with open(settings.MEDIA_ROOT + '/' + str(vcfile.file), encoding = 'UTF-8') as f:
            for line in f.readlines():
                file.append(line)
        # 历史文件
        for findpath, findfolders, findfiles in os.walk(fullpath):
            break
        history = []
        # history_id = sorted([fid for fid in findfiles if fid != str(vcfile.file).split('/')[-1]], reverse = True)
        history_id = sorted(findfiles, reverse = True)
        for i in range(1, len(history_id)):
            history.append([history_id[i], diff(findpath + '/' + history_id[i], findpath + '/' + history_id[i - 1])])

        context = {'code': 200, 'message': '打开文本成功！', 'file': file, 'language': language, 'filename': str(vcfile.file).split("/")[-2], 
                'history_id': history_id, 'history': history}
        return render(request, 'openfile.html', context)
