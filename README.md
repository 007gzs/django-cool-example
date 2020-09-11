# django-cool-example

本项目为[django-cool](http://github.com/007gzs/django-cool "django-cool")库的开发demo

[在线查看](https://example.django.cool/ "django-cool-example")

开始使用
----------

```
# 下载项目
git clone https://github.com/007gzs/django-cool-example.git
cd django-cool-example
# 安装依赖
pip install -r requirements.txt
# 初始化国际化
python manage.py compilemessages
# 初始化数据库
python manage.py makemigrations
python manage.py migrate
# 创建超管用户
python manage.py createsuperuser
# 在服务器上运行程序
sudo python manage.py runserver 0.0.0.0:80
```

测试页面
----------

- [所有接口api文档](https://example.django.cool/doc.html)
- [单个接口api文档](https://example.django.cool/api/demo/user/register)
- [后台演示](https://example.django.cool/admin) (用户名：demo 密码：django-cool)
