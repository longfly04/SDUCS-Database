from django.forms import Form
from django.forms import fields
from django.core.exceptions import ValidationError


from django.db.models import BooleanField as _BooleanField

# 重定义BooleanField的行为，在为其赋值时，自动将字符串以我们想要的规则转换成Bool值
class BooleanField(_BooleanField):
    def get_prep_value(self, value):
        if value in ("0", "false", "False"):
            return False
        elif  value in ("1", "true", "True"):
            return True
        else:
           return super(BooleanField, self).get_prep_value(value)


#-------------------------------------------- RegisterForm --------------------------------------------#
"""
    注册表单
"""
class RegisterForm(Form):
    # 用户名
    username = fields.CharField(
        required = True,
        min_length = 6,
        max_length = 15,
        error_messages = {
            'required':     '用户名不可以为空！',
            'min_length':   '用户名不能低于6位！',
            'max_length':   '用户名不能超过15位！'
        }
    )
    # 密码
    password1 = fields.CharField(
        required = True,
        min_length = 6,
        max_length = 18,
        error_messages = {
            'required':     '密码不可以空',
            'min_length':   '密码不能低于6位！',
            'max_length':   '密码不能超过18位！'
        }
    )
    password2 = fields.CharField(required=False)
    # 邮箱
    email = fields.EmailField(
        required = True,
        error_messages = {
            'required':     '邮箱不可以为空！'
        },
    )
    # 详细地址
    useraddress = fields.CharField(required = False)
    # 头像
    # userpicture = fields.ImageField(required = False)
    
    # 密码重复验证
    def clean_password2(self):
        if not self.errors.get('password1'):
            if self.cleaned_data['password2'] != self.cleaned_data['password1']:
                raise ValidationError("两次输入的密码不一致，请重新输入！")
            return self.cleaned_data



#-------------------------------------------- LoginForm --------------------------------------------#
"""
    登录表单
"""
class LoginForm(Form):
    # 用户名
    username = fields.CharField(
        required = True,
        min_length = 6,
        max_length = 15,
        error_messages = {
            'required':     '用户名不可以为空！',
            'min_length':   '用户名不能低于6位！',
            'max_length':   '用户名不能超过15位！'
        }
    )
    # 密码
    password = fields.CharField(
        required = True,
        error_messages = {
            'required':     '密码不可以空！'
        }
    )


#-------------------------------------------- CreateFolderForm --------------------------------------------#
"""
    新建文件夹表单
"""
class CreateFolder(Form):
    # 文件夹名
    folder = fields.CharField(
        required = True,
        error_messages = {
            'required':     '文件夹名称不可以为空！'
        }
    )


#-------------------------------------------- CreateRepoForm --------------------------------------------#
"""
    新建代码仓库表单
"""
class CreateRepo(Form):
    # 仓库名
    reponame = fields.CharField(
        required = True,
        error_messages = {
            'required':     '仓库名称不可以为空！'
        }
    )
    # 仓库开放状态
    state = fields.CharField(
        required = True,
        error_messages = {
            'required':     '仓库开放状态不可以为空！'
        }
    )
    # 仓库简介
    intro = fields.CharField(required = False)



#-------------------------------------------- SearchRepoForm --------------------------------------------#
"""
    搜索仓库表单
"""
class SearchRepo(Form):
    # 仓库名前缀
    reponame = fields.CharField(
        required = True,
        error_messages = {
            'required':     '仓库名称不可以为空！'
        }
    )



#-------------------------------------------- CreateIssueForm --------------------------------------------#
"""
    新建问题表单
"""
class CreateIssue(Form):
    # 问题主题
    topic = fields.CharField(
        required = True,
        error_messages = {
            'required':     '问题主题不可以为空！'
        }
    )


#-------------------------------------------- CreateProjectForm --------------------------------------------#
"""
    新建计划表单
"""
class CreateProject(Form):
    # 计划主题
    projTopic = fields.CharField(
        required = True,
        error_messages = {
            'required':     '计划主题不可以为空！'
        }
    )
    # 计划内容
    article = fields.CharField(
        required = True,
        error_messages = {
            'required':     '计划内容不可以为空！'
        }
    )
    # 截至时间
    time = fields.DateTimeField(
        required = True,
        error_messages = {
            'required':     '截止时间不可以为空！'
        }
    )


#-------------------------------------------- AddContributorForm --------------------------------------------#
"""
    新建贡献者表单
"""
class AddContributor(Form):
    # 计划主题
    username = fields.CharField(
        required = True,
        error_messages = {
            'required':     '用户名不可以为空！'
        }
    )

#-------------------------------------------- AddIssueTopicForm --------------------------------------------#
"""
    新建问题帖子表单
"""
class AddIssueTopic(Form):
    # 帖子内容
    article = fields.CharField(
        required = True,
        error_messages = {
            'required':     '帖子不可以为空！'
        }
    )
