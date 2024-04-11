"""
    模型模块        |   用户信息管理
    -----------------------------------------------------------------------------------------------------
    模型            |   属性
    -----------------------------------------------------------------------------------------------------
    


"""

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User, AbstractUser, AbstractBaseUser,PermissionsMixin,BaseUserManager
from shortuuidfield import ShortUUIDField
from django.utils.deconstruct import deconstructible
from django.utils import timezone
from django.conf import settings

import os
import datetime
import uuid
import zipfile
import zipstream
from io import StringIO


from django.db.models import BooleanField as _BooleanField

# 重定义BooleanField的行为，在为其赋值时，自动将字符串以我们想要的规则转换成Bool值
class BooleanField(_BooleanField):
    def get_prep_value(self, value):
        if value in ("0", "false", "False"):
            return False
        elif value in ("1", "true", "True"):
            return True
        else:
           return super(BooleanField, self).get_prep_value(value)


#-------------------------------------------- RegionGlobal --------------------------------------------#
"""
    表名    |   RegionGlobal
    ---------------------------------------------------------------------------
    属性            |   属性介绍
    ---------------------------------------------------------------------------
    id              |   顺序主键
    pid             |   父节点id
    path            |   完整路径，由逗号隔开
    level           |   所在层级
    name            |   中文名称
    name_en         |   英文名称
    name_pinyin     |   拼音名称
    code            |   地区代码
    ---------------------------------------------------------------------------

"""
class RegionGlobal(models.Model):
    # 该表为原有表，自动导入

    # 设置字段
    
    # ID                主键
    ID          = models.BigAutoField(auto_created = True, primary_key = True, serialize = False, verbose_name = 'ID')
    # 父节点ID          非负整数                
    pid         = models.PositiveIntegerField(blank = True, null = True)
    # 完整路径          255位字符串         由逗号隔开
    path        = models.CharField(max_length = 255, blank = True, null = True)
    # 层级              非负整数            
    level       = models.PositiveIntegerField(blank = True, null = True)
    # 名称（中文）      255位字符串
    name        = models.CharField(max_length = 255, blank = True, null = True)
    # 名称（英文）      255位字符串
    name_en     = models.CharField(max_length = 255, blank = True, null = True)
    # 名称（拼音）      255位字符串
    name_pinyin = models.CharField(max_length = 255, blank = True, null = True)
    # 地区代码          50位字符串
    code        = models.CharField(max_length = 50, blank = True, null = True)

    class Meta:
        managed = True
        db_table = 'region_global'

    def __str__(self):
        return str(self.ID) + ' ' + self.name + ' ' + self.name_en


# 自定义用户类型和相应管理模块，包括用户检验、注册、退出等
# 参考：https://blog.csdn.net/weixin_44951273/article/details/101028522


#-------------------------------------------- UserManager --------------------------------------------#
"""
    自定义UserManager用户管理器，继承自BaseUserManager
"""
class UserManager(BaseUserManager):
    def _create_user(self, username, password, email, **kwargs):
        if not username:
            raise ValueError("请输入用户名！")
        if not password:
            raise ValueError("请输入密码！")
        if not email:
            raise ValueError("请输入邮箱地址！")
        user = self.model(userName = username, userEmail = email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    # 创建普通用户
    def create_user(self, username, password, email, **kwargs):
        kwargs['is_superuser'] = False
        return self._create_user(username, password, email, **kwargs)

    # 创建超级用户
    def create_superuser(self, username, password, email, **kwargs):
        kwargs['is_superuser'] = True
        kwargs['is_staff'] = True
        return self._create_user(username, password, email, **kwargs)



#------------------------------------------------ User ------------------------------------------------#
"""
    表名    |   User
    ---------------------------------------------------------------------------
    属性            |   属性介绍
    ---------------------------------------------------------------------------



"""
class User(AbstractBaseUser, PermissionsMixin):
    # 继承自AbstractBaseUser，PermissionsMixin，重写User模型
    
    # 设置字段

    # 用户ID            ShortUUID       主键
    userID          = ShortUUIDField(primary_key = True)
    # 用户昵称          15位字符串      非空唯一
    userName        = models.CharField(max_length = 15, unique = True, verbose_name = '用户名')
    # 用户年龄          整数            0 - 200
    userAge         = models.IntegerField(validators = [MinValueValidator(0), MaxValueValidator(200)], blank = True, null = True, verbose_name = '年龄')
    # 用户性别          2位字符串       0: 未知  1: 男性  2: 女性        
    GENDER_TYPE     = ((0, '未知'), ("1","男"), ("2","女"))
    userGENDER      = models.CharField(max_length = 2, choices = GENDER_TYPE, verbose_name = '性别')
    # 用户手机          11位字符串      
    userPhone       = models.CharField(max_length = 11, null = True, blank = True, verbose_name = '手机号码')
    # 用户邮箱          Email
    userEmail       = models.EmailField(null = True, blank = True, verbose_name = '邮箱')
    # 用户头像          Image
    def user_directory_path(instance, filename):
        ext = filename.split('.')[-1]
        filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
        # return the whole path to the file
        return os.path.join('user_picture', instance.user.id, filename)
    userPicture     = models.ImageField(upload_to = user_directory_path, null = True, blank = True, verbose_name = '用户头像')
    # 地址：国家        非负整数        与RegionGlobal关联id，但不使用数据库层次的外码约束
    userCountry     = models.ForeignKey(RegionGlobal, related_name = 'country_related', on_delete = models.CASCADE, default = 7, db_constraint = False, verbose_name = '国家')
    # 地址：省份        非负整数        与RegionGlobal关联id，但不使用数据库层次的外码约束
    userProvince    = models.ForeignKey(RegionGlobal, related_name = 'province_related', on_delete = models.CASCADE, default = 247, db_constraint = False, verbose_name = '省份')
    # 地址：城市        非负整数        与RegionGlobal关联id，但不使用数据库层次的外码约束
    userCity        = models.ForeignKey(RegionGlobal, related_name = 'city_related', on_delete = models.CASCADE, default = 3021, db_constraint = False, verbose_name = '城市')
    # 详细地址          255位字符串
    userAddress     = models.CharField(max_length = 255, blank = True, null = True, verbose_name = '详细地址')
    # 创建时间          日期            新增时生效
    userCreateTime  = models.DateTimeField(auto_now_add = True, verbose_name = '创建时间') 
    # 激活状态          布尔类型
    is_active       = models.BooleanField(default = True, verbose_name = '激活状态')
    # 管理员权限        布尔类型
    is_staff        = models.BooleanField(default = True ,verbose_name = '管理员权限')

    # 使用authenticate验证时使用的验证字段
    USERNAME_FIELD  = 'userName'
    # 创建用户时必须填写的字段，包括password和USERNAME_FIELD
    REQUIRED_FIELDS = ['userEmail']
    # 发送邮件时使用的字段
    EMAIL_FIELD = 'userEmail'

    # 导入自定义Manager
    objects = UserManager()

    # 指定表名
    class Meta:
        db_table = 'User'
        managed = True

    # 简略信息
    def __str__(self):
        return self.userName



# 自定义文件夹及文件夹管理类
# 参考：https://www.cnblogs.com/chaoqi/p/11920767.html

#-------------------------------------------- File Manager --------------------------------------------#
"""
    自定义文件管理类，包括：
    ----FilePath        文件夹类，根据相对路径产生并创建绝对路径文件夹
    ----savefile        文件储存函数，根据指定的相对路径在项目中储存文件，并使用时间戳标识
    ----VCFiles         自定义文件类，包含路径和文件对象，适用于views中进行文件储存和访问
"""
@deconstructible
class FilePath(object):
    def __init__(self, sub_path):
        self.path = sub_path                    # 要创建的文件夹名称
        self.full_path = '{root}/{path}'.format(root = settings.MEDIA_ROOT, path = sub_path)    # 拼接 settings 中设置的根目录
        
        if not os.path.exists(self.full_path):  # 检查拼接的路径是否被创建，如果没有就创建新文件夹
            os.makedirs(self.full_path)

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        t = timezone.now().strftime('%Y%m%d%H%M%S%f')

        if instance.pk:
            filename = '{}-{}.{}'.format(instance.pk, t, ext)
        else:
            filename = '{}.{}'.format(t, ext)
        return os.path.join(self.path, filename)


# 自定义文件储存方法，将文件储存在指定路径中
# 相对路径为 file_name = 'path/[userID/]time.name'
# 绝对路径为 full_name = 'MEDIA_ROOT/path/[userID/]time.name'
def savefile(files, path, user = None):
    if user:            # 是否使用用户id作为文件存储路径
        file_name = '{path}/{id}'.format(path = path, id = user.userID)   
        if not os.path.exists(settings.MEDIA_ROOT + '/' + file_name):       # 没有该路径则创建
            os.makedirs(settings.MEDIA_ROOT + '/' + file_name)
        file_name = file_name + '/{time}.{name}'.format(time = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"), name = files.name.split(".")[-1])
    else:
        if not os.path.exists(settings.MEDIA_ROOT + '/' + path):       # 没有该路径则创建
            os.makedirs(settings.MEDIA_ROOT + '/' + path)
        file_name = '{path}/{time}.{name}'.format(path = path, time = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"), name = files.name.split(".")[-1])
    full_name = '{root}/{filename}'.format(root = settings.MEDIA_ROOT, filename = file_name)
    with open(full_name, 'wb+') as f:       # 将文件存储到项目中
        for chunk in files.chunks():
            f.write(chunk)
    return file_name, full_name


# 利用zipstream实现的压缩包下载文件夹
# 参考：https://zhengxingtao.com/article/96/
class ZipUtilities(object):
    """
    将文件或者文件夹打包成ZIP格式的文件，然后下载，在后台可以通过response完成下载
    """
    zip_file = None

    def __init__(self):
        self.zip_file = zipstream.ZipFile(mode = 'w', compression = zipstream.ZIP_DEFLATED)

    def to_zip(self, file, name):
        if os.path.isfile(file):
            self.zip_file.write(file, arcname = os.path.basename(file))
        else:
            self.add_folder_to_zip(file, name)

    def add_folder_to_zip(self, folder, name):
        if os.path.isfile(folder):
            self.zip_file.write(folder, arcname = name)
        else:
            for file in os.listdir(folder):
                full_path = os.path.join(folder, file)
                if os.path.isfile(full_path):
                    self.zip_file.write(
                        full_path,
                        arcname = os.path.join(name, os.path.basename(full_path))
                    )
                elif os.path.isdir(full_path):
                    self.add_folder_to_zip(
                        full_path,
                        os.path.join(name, os.path.basename(full_path))
                    )

    def close(self):
        if self.zip_file:
            self.zip_file.close()


# zip文件处理
class MemoryZipFile(object):
    def __init__(self):
        # 创建内存文件
        self._memory_zip = StringIO()

    def append_file(self, filename_in_zip, local_file_full_path):
        """
        description:写文件内容到zip
        注意这里的第二个参数是本地磁盘文件的全路径:
            windows: c:/demo/1.jpg
            linux: /usr/local/test/1.jpg
        """
        zf = zipfile.ZipFile(self._memory_zip, "a", zipfile.ZIP_DEFLATED, False)
        zf.write(local_file_full_path, filename_in_zip)
        for zfile in zf.filelist:
            zfile.create_system = 0
        return self

    def read(self):
        """
        description: 读取zip文件内容
        """
        self._memory_zip.seek(0)
        return self._memory_zip.read()



#--------------------------------------------- VCFiles ---------------------------------------------#
"""
    表名    |   VCFiles
    ---------------------------------------------------------------------------
    属性            |   属性介绍
    ---------------------------------------------------------------------------



"""
class VCFiles(models.Model):
    filepath = FilePath('repository')                           # 该表的文件存储路径
    def user_directory_path(instance, filename):
        pass
    # 储存的文件
    file = models.FileField(upload_to = user_directory_path, null = True, blank = True, verbose_name = '文件', max_length = 1000)

    class Meta:
        db_table = 'VCFiles'
        managed = True

    def __str__(self):
        return self.file.name




#--------------------------------------------- Repository ---------------------------------------------#
"""
    表名    |   Repository
    ---------------------------------------------------------------------------
    属性            |   属性介绍
    ---------------------------------------------------------------------------



"""
class Repository(models.Model):

    # 库ID              ShortUUID       主键
    rID             = ShortUUIDField(primary_key = True)
    # 库名（根目录）    100位字符串     非空唯一
    rName           = models.CharField(max_length = 100, unique = True, verbose_name = '库名')
    # 仓库开放状态      BooleanField
    rState          = models.BooleanField(default = False, verbose_name = '仓库开放状态')
    # 库简介            1000位字符串
    rIntro          = models.CharField(max_length = 1000, blank = True, null = True, verbose_name = '库介绍')

    # 指定表名
    class Meta:
        db_table = 'Repository'
        managed = True
    
    # 简略信息
    def __str__(self):
        return self.rName + ' ' + str(self.rState)


#--------------------------------------------- User_Repository ---------------------------------------------#
"""
    表名    |   User_Repository
    ---------------------------------------------------------------------------
    属性            |   属性介绍
    ---------------------------------------------------------------------------



"""
class UserRepository(models.Model):

    # 用户_库ID         ShortUUID       主键
    urID            = ShortUUIDField(primary_key = True)
    # 用户ID            非负整数        与User关联id，但不使用数据库层次的外码约束
    uID             = models.ForeignKey(User, related_name = 'ru_uid_related', on_delete = models.CASCADE, db_constraint = False, verbose_name = '用户ID')
    # 库ID              非负整数        与Repository关联id，但不使用数据库层次的外码约束
    rID             = models.ForeignKey(Repository, related_name = 'ru_rid_related', on_delete = models.CASCADE, db_constraint = False, verbose_name = '库ID')

    # 指定表名，设置多字段主键
    # 参考：https://docs.djangoproject.com/en/dev/ref/models/options/#unique-together
    class Meta:
        db_table = 'User_Repository'
        unique_together = [['uID', 'rID']]
        managed = True
    
    # 简略信息
    def __str__(self):
        return str(self.uID) + ' ' + str(self.rID)



#--------------------------------------------- Issue_UR ---------------------------------------------#
"""
    表名    |   Issue_UR
    ---------------------------------------------------------------------------
    属性            |   属性介绍
    ---------------------------------------------------------------------------



"""
class Issue_UR(models.Model):

    # 问题ID            ShortUUID       主键
    iID             = ShortUUIDField(primary_key = True)
    # 用户ID            非负整数        与User关联id，但不使用数据库层次的外码约束
    uID             = models.ForeignKey(User, related_name = 'iru_uid_related', on_delete = models.CASCADE, db_constraint = False, verbose_name = '用户ID')
    # 库ID              非负整数        与Repository关联id，但不使用数据库层次的外码约束
    rID             = models.ForeignKey(Repository, related_name = 'iru_rid_related', on_delete = models.CASCADE, db_constraint = False, verbose_name = '库ID')
    # 状态              BooleanField
    iState          = models.BooleanField(default = True, verbose_name = '问题开放状态')
    # 主题              200位字符串     非空唯一
    iTopic          = models.CharField(max_length = 200, unique = True, verbose_name = '问题名称')
    # 时间              DateTimeField
    itime           = models.DateTimeField(auto_now_add = True, verbose_name = '创建问题时间') 

    class Meta:
        db_table = 'Issue_UR'
        managed = True
    
    # 简略信息
    def __str__(self):
        return self.iTopic


#--------------------------------------------- Issues ---------------------------------------------#
"""
    表名    |   Issues
    ---------------------------------------------------------------------------
    属性            |   属性介绍
    ---------------------------------------------------------------------------



"""
class Issues(models.Model):
    # 帖子ID            ShortUUID       主键
    itID            = ShortUUIDField(primary_key = True)
    # 问题ID            非负整数        与Issue_UR关联，但不使用数据库层次的外码约束
    iID             = models.ForeignKey(Issue_UR, related_name = 'i_iid_related', on_delete = models.CASCADE, db_constraint = False, verbose_name = '问题ID')
    # 问题发起人        非负整数        与User关联id，但不使用数据库层次的外码约束
    iuid            = models.ForeignKey(User, related_name = 'i_uid_related', on_delete = models.CASCADE, db_constraint = False, verbose_name = '用户ID')
    # 帖子内容          1000位字符串    非空
    article         = models.CharField(max_length = 1000, verbose_name = '帖子内容')
    # 创建时间          DateTimeField
    time            = models.DateTimeField(auto_now_add = True, verbose_name = '回帖时间') 

    class Meta:
        db_table = 'Issues'
        managed = True
    
    # 简略信息
    def __str__(self):
        return str(self.iID) + '\n' + self.article



#--------------------------------------------- Projects ---------------------------------------------#
"""
    表名    |   Projects
    ---------------------------------------------------------------------------
    属性            |   属性介绍
    ---------------------------------------------------------------------------



"""
class Projects(models.Model):
    # 计划ID            ShortUUID       主键
    projID          = ShortUUIDField(primary_key = True)
    # 库ID              非负整数        与Repository关联id，但不使用数据库层次的外码约束
    rID             = models.ForeignKey(Repository, related_name = 'proj_rid_related', on_delete = models.CASCADE, db_constraint = False, verbose_name = '库ID')
    # 计划主题          1000位字符串    非空
    projTopic       = models.CharField(max_length = 1000, verbose_name = '计划主题')
    # 计划内容          1000位字符串    非空
    article         = models.CharField(max_length = 1000, verbose_name = '计划内容')
    # 截止时间          DateTimeField
    time            = models.DateTimeField(verbose_name = '计划时间') 

    class Meta:
        db_table = 'Projects'
        managed = True
    
    # 简略信息
    def __str__(self):
        return self.projTopic + '\n' + self.article





