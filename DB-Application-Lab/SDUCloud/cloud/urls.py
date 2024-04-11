from django.urls import path, re_path

from . import views

urlpatterns = [
    # 初始界面
    # ex: 
    path('', views.site, name = 'site'),
    
    # 注册
    # ex: /user/register/
    path('user/register', views.register, name = 'register'),

    # 登录
    # ex: /user/login
    path('user/login', views.signin, name = 'login'),
    # ex: /user/login?next=/path...
    re_path(r'^user/login\?next=(?P<nextpath>(.+))$', views.signin, name = 'login'),

    # 退出
    # ex: /user/exit
    path('user/exit', views.exit, name = 'exit'),

    # 用户界面
    # ex: /user/index
    path('user/index', views.index, name = 'index'), 
    # ex: /user/name/index
    re_path(r'^user/(?P<username>(.+))/index$', views.index, name = 'index'),

    # 上传文件
    # ex: repository/path.../upload
    re_path(r'^repository/(?P<repo>(\w+))/(?P<path>(.*))/upload$', views.upload, name = 'upload'),
    re_path(r'^repository/(?P<repo>(\w+))/upload$', views.upload, name = 'upload'),

    # 下载文件
    # ex: repository/path.../download
    re_path(r'^repository/(?P<repo>(\w+))/(?P<path>(.*))/download$', views.download, name = 'download'),
    re_path(r'^repository/(?P<repo>(\w+))/download$', views.download, name = 'download'),
    # ex: repository/path.../filedownload
    re_path(r'^repository/(?P<repo>(\w+))/(?P<path>(.*))/filedownload$', views.filedownload, name = 'filedownload'),

    # 删除文件
    # ex: repository/path.../delete
    re_path(r'^repository/(?P<repo>(\w+))/(?P<path>(.*))/delete$', views.delete, name = 'delete'),
    re_path(r'^repository/(?P<repo>(\w+))/delete$', views.delete, name = 'delete'),

    # 新建文件夹
    # ex: repository/path.../newfolder
    re_path(r'^repository/(?P<repo>(\w+))/(?P<path>(.*))/newfolder$', views.newfolder, name = 'newfolder'),
    re_path(r'^repository/(?P<repo>(\w+))/newfolder$', views.newfolder, name = 'newfolder'),

    # 创建仓库
    # ex: repository/createrepo
    path('repository/createrepo', views.create_repo, name = 'createrepo'),

    # 搜索仓库
    # ex: repository/searchrepo
    path('repository/searchrepo', views.search_repo, name = 'search_repo'),

    # 访问仓库
    # ex: repository/repo[/path...]/view
    re_path(r'^repository/(?P<repo>(\w+))/view$', views.view_repo, name = 'viewrepo'),
    re_path(r'^repository/(?P<repo>(\w+))/(?P<path>(.*))/view$', views.view_repo, name = 'viewrepo'),

    # 修改仓库状态
    # ex: repository/repo/changestate
    re_path(r'^repository/(?P<repo>(\w+))/changestate$', views.change_state, name = 'changestate'),

    # 新增贡献者
    # ex: repository/repo/addcontributor
    re_path(r'^repository/(?P<repo>(\w+))/addcontributor$', views.add_contributor, name = 'addcontributor'),

    # 打开文件
    # ex: repository/repo/path.../openfile
    re_path(r'^repository/(?P<repo>(\w+))/(?P<path>(.*))/openfile$', views.open_file, name = 'openfile'),

    # 查看历史文本文件并比较异同
    # ex: repository/repo/path.../difffile
    re_path(r'^repository/(?P<repo>(\w+))/(?P<path>(.*))/difffile$', views.diff_file, name = 'difffile'),

    # 创建问题
    # ex: repository/repo/createissue
    re_path(r'^repository/(?P<repo>(\w+))/createissue$', views.create_issue, name = 'createissue'),

    # 列出问题
    # ex: repository/repo/viewissue
    re_path(r'^repository/(?P<repo>(\w+))/viewissue$', views.list_issue, name = 'listissue'),

    # 查看问题
    # ex: repository/repo/viewissue/topic
    re_path(r'^repository/(?P<repo>(\w+))/viewissue/(?P<topic>(\w+))$', views.view_issue, name = 'viewissue'),

    # 新增问题帖子
    # ex: repository/repo/viewissue/topic/addtopic
    re_path(r'^repository/(?P<repo>(\w+))/viewissue/(?P<topic>(\w+))/addtopic$', views.add_issue_topic, name = 'addissuetopic'),

    # 更改问题开放状态
    # ex: repository/repo/viewissue/topic/changestate
    re_path(r'^repository/(?P<repo>(\w+))/viewissue/(?P<topic>(\w+))/changestate$', views.change_issue_state, name = 'changeissuestate'),

    # 查看计划
    # ex: repository/repo/project/viewproject
    re_path(r'^repository/(?P<repo>(\w+))/project/viewproject$', views.view_project, name = 'view_project'),

    # 新建计划
    # ex: repository/repo/project/createproject
    re_path(r'^repository/(?P<repo>(\w+))/project/createproject$', views.create_project, name = 'create_project'),

]