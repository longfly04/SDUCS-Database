# setting中的配置默认为sqlite3数据库
# 在setting.py的同级目录的 __init__.py 加入如下配置：

import pymysql

pymysql.install_as_MySQLdb()