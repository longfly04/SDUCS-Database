# SDUCloud代码托管平台

## 简介
本案例的设计理念源于对实际业务需求的深刻理解，模拟了一个真实的代码托管环境。

作者：
山东大学计算机科学与技术学院
褚耀辉   
于龙飞   
杨伟钦   
彭朝晖   


## 项目结构
SDUCloud
│
├── cloud                       # cloud app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py                     # 设置app名
│   ├── files.py                    # 文件上传、下载、删除管理模块
│   ├── form.py                     # 表单格式
│   ├── issues.py                   # 问题管理模块
│   ├── models.py                   # 数据库关系模式
│   ├── project.py                  # 计划管理模块
│   ├── repo.py                     # 仓库管理模块、历史文件管理模块
│   ├── tests.py
│   ├── urls.py                     # URL匹配模式
│   ├── users.py                    # 用户管理模块
│   └── views.py                    # 视图总体管理
│
├── dbimport
│   └── region_global.sql
│
├── static                      # 静态文件，可被前端访问
│   ├── media                       # media中储存用户文件
│   │   ├── picture                 # 用户头像
│   │   └── repository              # 代码仓库文件
│   │
│   └── static                      # 项目static文件，主要是前端配置
│       ├── css
│       ├── images                  # 网站背景和默认头像
│       ├── img
│       ├── js
│       ├── partials
│       ├── scss
│       └── timeline3               # timelineJS3，用于时间轴配置
│
├── templates                   # 前端模板(templates)文件
│   ├── addcontributor.html         # 新增贡献者
│   ├── addissue.html               # 新增问题帖子
│   ├── createissue.html            # 新增问题
│   ├── createrepo.html             # 建库
│   ├── createtimeline.html         # 新增时间轴计划
│   ├── index.html                  # 用户信息
│   ├── listissue.html              # 代码仓库问题列表
│   ├── login.html                  # 登录界面
│   ├── newfolder.html              # 新建文件夹
│   ├── openfile.html               # 打开文本文件
│   ├── pagejump.html               # 页面跳转
│   ├── register.html               # 注册界面
│   ├── repository.html             # 代码仓库界面
│   ├── searchrepo.html             # 搜索仓库
│   ├── timeline.html               # 时间轴（计划）界面
│   ├── upload.html                 # 上传文件界面
│   ├── viewissue.html              # 问题帖子列表
│   └── welcome.html                # 欢迎界面
│
├── VCLOUD                      # 项目设置
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                 # 项目全局配置设置
│   ├── urls.py                     # app url分发管理
│   └── wsgi.py
│
├── manage.py                   # 项目管理器
└── README.md
