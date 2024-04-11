# 文件管理模块

from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

import os
import re

import shutil

from .models import *
from .form import *


# 文件上传接口
@login_required
def upload(request, repo, path = ''):
    if request.method == 'GET':
        return render(request, 'upload.html')
    
    file = request.FILES.get('file', None)
    if file:
        # 检查用户是否为仓库贡献者
        try:
            ur = UserRepository.objects.get(uID = request.user.userID, rID = Repository.objects.get(rName = repo))
        except:
            if path:
                context = {'code': 400, 'message': '上传失败！没有找到仓库或没有修改权限！', 'next_url': '/repository/{repo}/{path}/view'.format(repo = repo, path = path)}
            else:
                context = {'code': 400, 'message': '上传失败！没有找到仓库或没有修改权限！', 'next_url': '/repository/{repo}/view'.format(repo = repo)}
            return render(request, 'pagejump.html', context)
        else:
            # 不使用用户ID作为上传路径，直接将文件名作为文件夹，储存多份以时间戳命名的历史文件
            if path != '':
                path = repo + '/' + path
            else:
                path = repo
            # 删除数据库中原有同名文件
            file_name, full_name = savefile(file, 'repository/' + path + '/' + file.name)
            try:
                f =  VCFiles.objects.get(file__startswith = 'repository/' + path + '/' + file.name)
                f.delete()
            except:
                pass
            VCFiles.objects.create(file = file_name)
            context = {'code': 200, 'message': '文件上传完成！Repository: {repo}  File path: {path}'.format(repo = repo, path = path + '/' + file.name), 
                    'next_url': '/repository/{path}/view'.format(path = path)}
            return render(request, 'pagejump.html', context)
    else:
        if path:
            context = {'code': 400, 'message': '上传失败！没有上传文件！', 'next_url': '/repository/{repo}/{path}/view'.format(repo = repo, path = path)}
        else:
            context = {'code': 400, 'message': '上传失败！没有上传文件！', 'next_url': '/repository/{repo}/view'.format(repo = repo)}
        return render(request, 'pagejump.html', context)



# 文件下载接口
# 更多不同的下载方法参考：https://zhengxingtao.com/article/96/
@login_required
def download(request, repo, path = ''):
    try:
        r = Repository.objects.get(rName = repo)
    except:
        context = {'code': 400, 'message': '下载失败！没有找到仓库！The path is: ' + repo + '/' + path, 'next_url': '/repository/searchrepo'}
        return render(request, 'pagejump.html', context)
    # 检查仓库是否公开，或者允许贡献者下载非公开仓库
    state = r.rState
    if not state:
        try:
            ur = UserRepository.objects.get(uID = request.user.userID, rID = Repository.objects.get(rName = repo))
        except:
            context = {'code': 400, 'message': '下载失败！仓库非公开或者你不是贡献者！The path is: ' + repo + '/' + path, 'next_url': '/repository/searchrepo'}
            return render(request, 'pagejump.html', context)
    files = VCFiles.objects.filter(file__startswith = 'repository/{repo}/{path}'.format(repo = repo, path = path))
    # 文件路径不存在
    if not files:
        context = {'code': 400, 'message': '下载失败！没有找到相应的文件路径！The path is: ' + repo + '/' + path, 'next_url': '/repository/{repo}/view'.format(repo = repo)}
        return render(request, 'pagejump.html', context)
    # 通过内存的方式打包下载文件
    utilities = ZipUtilities()
    for file in files:
        folder_path = settings.MEDIA_ROOT + '/' + re.findall(r'(.*/).*', str(file.file))[0]
        folder_name = re.findall(r'repository/(.*)/.*', str(file.file))[0]
        # utilities.add_folder_to_zip(folder_path, folder_name)
        utilities.add_folder_to_zip(settings.MEDIA_ROOT + '/' + str(file), folder_name)
        # utilities.close()             # 注意：这里关闭内存的话，数据没法返回
    response = StreamingHttpResponse(
        utilities.zip_file, 
        content_type = 'application/zip'
    )
    response['Content-Disposition'] = \
        'attachment;filename="{name}.zip"'.format(name = repo + '/' + path)
    return response


# 单一文件下载
# 参考：https://www.cnblogs.com/fengting0913/p/14005826.html
@login_required
def filedownload(request, repo, path = ''):
    try:
        r = Repository.objects.get(rName = repo)
    except:
        context = {'code': 400, 'message': '下载失败！没有找到仓库！The path is: ' + repo + '/' + path, 'next_url': '/repository/searchrepo'}
        return render(request, 'pagejump.html', context)
    
    # 检查仓库是否公开，或者允许贡献者下载非公开仓库
    state = r.rState
    if not state:
        try:
            ur = UserRepository.objects.get(uID = request.user.userID, rID = Repository.objects.get(rName = repo))
        except:
            context = {'code': 400, 'message': '下载失败！仓库非公开或者你不是贡献者！The path is: ' + repo + '/' + path, 'next_url': '/repository/searchrepo'}
            return render(request, 'pagejump.html', context)
    files = VCFiles.objects.filter(file__startswith = 'repository/{repo}/{path}'.format(repo = repo, path = path))
    # 文件路径不存在
    if not files:
        context = {'code': 400, 'message': '下载失败！没有找到相应的文件路径！The path is: ' + repo + '/' + path, 'next_url': '/repository/{repo}/view'.format(repo = repo)}
        return render(request, 'pagejump.html', context)
    # 直接下载单个文件
    if len(files) != 1:
        context = {'code': 400, 'message': '打开的不是文件！', 'next_url': '/repository/{repo}/view'.format(repo = repo)}
        return render(request, 'pagejump.html', context)
    
    def down_chunk_file_manager(file_path, chuck_size = 1024):
        with open(file_path, "rb") as file:
            while True:
                chuck_stream = file.read(chuck_size)
                if chuck_stream:
                    yield chuck_stream
                else:
                    break
   
    file_path = settings.MEDIA_ROOT + '/' + str(VCFiles.objects.get(file__startswith = 'repository/{repo}/{path}'.format(repo = repo, path = path)).file)
    filename = str(file_path).split("/")[-2]
    response = StreamingHttpResponse(down_chunk_file_manager(file_path))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(filename)

    return response


# 文件删除
@login_required
def delete(request, repo, path = ''):
    try:
        r = Repository.objects.get(rName = repo)
    except:
        context = {'code': 400, 'message': '删除失败！没有找到仓库！The path is: ' + repo + '/' + path, 'next_url': '/repository/searchrepo'}
        return render(request, 'pagejump.html', context)
    # 检查用户是否为仓库贡献者
    try:
        ur = UserRepository.objects.get(uID = request.user.userID, rID = Repository.objects.get(rName = repo))
    except:
        if path:
            context = {'code': 400, 'message': '删除失败！没有修改权限！', 'next_url': '/repository/{repo}/{path}/view'.format(repo = repo, path = path)}
        else:
            context = {'code': 400, 'message': '删除失败！没有修改权限！', 'next_url': '/repository/{repo}/view'.format(repo = repo)}
        return render(request, 'pagejump.html', context)
    files = VCFiles.objects.filter(file__startswith = 'repository/{repo}/{path}'.format(repo = repo, path = path))
    # 文件路径不存在
    if not files:
        context = {'code': 400, 'message': '删除失败！没有找到相应的文件路径！The path is: ' + repo + '/' + path, 'next_url': '/repository/{repo}/view'.format(repo = repo)}
        return render(request, 'pagejump.html', context)
    # 删除文件或文件夹
    file_path = settings.MEDIA_ROOT + '/' + 'repository/{repo}/{path}'.format(repo = repo, path = path)
    shutil.rmtree(file_path)
    # os.rmdir(file_path)
    files.delete()
    if path.split('/')[: -2]:
        context = {'code': 200, 'message': '删除成功！', 'next_url': '/repository/{repo}/{path}/view'.format(repo = repo, path = ''.join(path.split('/')[: -2]))}
    else:
        context = {'code': 200, 'message': '删除成功！', 'next_url': '/repository/{repo}/view'.format(repo = repo)}

    return render(request, 'pagejump.html', context)


# 新建文件夹
@login_required
def newfolder(request, repo, path = ''):
    if request.method == 'GET':
        return render(request, 'newfolder.html')

    try:
        r = Repository.objects.get(rName = repo)
    except:
        context = {'code': 400, 'message': '新建失败！没有找到仓库！The path is: ' + repo + '/' + path, 'next_url': '/repository/searchrepo'}
        return render(request, 'pagejump.html', context)
    # 检查用户是否为仓库贡献者
    try:
        ur = UserRepository.objects.get(uID = request.user.userID, rID = Repository.objects.get(rName = repo))
    except:
        if path:
            context = {'code': 400, 'message': '新建失败！没有修改权限！', 'next_url': '/repository/{repo}/{path}/view'.format(repo = repo, path = path)}
        else:
            context = {'code': 400, 'message': '新建失败！没有修改权限！', 'next_url': '/repository/{repo}/view'.format(repo = repo)}
        return render(request, 'pagejump.html', context)
    # 新建文件夹
    form = CreateFolder(request.POST)
    if form.is_valid():
        folder = form.cleaned_data['folder']
        if path:
            context = {'code': 200, 'message': '新建文件夹成功！还需要向文件夹上传文件哦！', 'next_url': '/repository/{repo}/{path}/{folder}/upload'.format(repo = repo, path = path, folder = folder)}
        else:
            context = {'code': 200, 'message': '新建文件夹成功！还需要向文件夹上传文件哦！', 'next_url': '/repository/{repo}/{folder}/upload'.format(repo = repo, folder = folder)}
    else:
        if path:
            context = {'code': 400, 'message': '新建文件夹失败！名称填写格式错误！', 'next_url': '/repository/{repo}/{path}/newfolder'.format(repo = repo, path = path)}
        else:
            context = {'code': 400, 'message': '新建文件夹失败！名称填写格式错误！', 'next_url': '/repository/{repo}/newfolder'.format(repo = repo)}
    return render(request, 'pagejump.html', context)

