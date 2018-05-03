# Django Celery 配置实践
基于django 2.0.4 的 djcelery 配置示例。

[TOC]

## 所需环境

python 3.5.2

rabbitmq

### 安装所需的包

`pip install -r requirements.txt`

## QuickStart

### 创建Django项目

创建一个名为proj的Django项目

`django-admin startproject proj`

### 创建Django App

创建一个用于演示的django app，这里名为demo

`django-admin startapp demo`

在创建的app中，增加tasks.py文件，用于编写celery任务

### 基础配置项目

修改proj/settings.py配置文件，增加celery相关配置。

#### 增加djcelery app

修改settings.py中INSTALLED_APPS，增加djcelery及app

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djcelery',
    'demo'
]
```

#### celery相关的参数配置

如果仅仅需求使用celery异步执行任务的话，以下最基础的配置就可以满足需求

```python
# 导入tasks文件，因为我们使用autodiscover_tasks
# 会自动导入每个app下的tasks.py，所以这个配置不是很必要
# 如果需要导入其他非tasks.py的模块，则需要再此配置需要导入的模块
# CELERY_IMPORTS = ('demo.tasks', )
# 配置 celery broker
CELERY_BROKER_URL = 'amqp://user:password@127.0.0.1:5672//'
# 配置 celery backend 用Redis会比较好
# 因为手上没有redis服务器，所以演示时用RabbitMQ替代
CELERY_RESULT_BACKEND = 'amqp://user:password@127.0.0.1:5672//'
```

### 创建Celery实例

在proj目录下，编辑celery.py文件，用于创建celery实例

```python
from celery import Celery
from django.conf import settings

# 创建celery应用
celery_app = Celery('proj', broker=settings.CELERY_BROKER_URL)
# 从配置文件中加载除celery外的其他配置
celery_app.config_from_object('django.conf:settings')
# 自动检索每个app下的tasks.py
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
```

### 编写异步任务

在之前创建的demo/tasks.py中，编写一个用于演示的异步任务。

注意每个异步任务之前都需要使用@celery_app.task装饰器。

celery_app实际是之前在proj/celery.py中创建的celery的实例，如果你的实例名称不一样，做对应的修改即可。

```Python
import logging
from proj.celery import celery_app

@celery_app.task
def async_task():
    logging.info('run async_task')
```

### 调用异步任务

在demo/views.py中定义一个页面，只用来调用异步任务。

```python
from django.http import HttpResponse
from demo.tasks import async_demo_task

# Create your views here.
def demo_task(request):
	# delay表示将任务交给celery执行
    async_demo_task.delay()
    return HttpResponse('任务已经运行')
```

在proj/urls.py中注册对应的url。

```python
from django.contrib import admin
from django.urls import path
from demo.views import demo_task

urlpatterns = [
    path('admin/', admin.site.urls),
    path('async_demo_task', demo_task),
]
```

### 启动Celery Worker

使用命令启动worker：

`manage.py celery -A proj worker -l info`

对参数做个简单的说明：

-A proj是指项目目录下的celery实例。演示项目名为proj，所以-A的值是proj。如果项目名是其他名字，将proj换成项目对应的名字。

-l info 是指日志记录的级别，这里记录的是info级别的日志。

如果配置没有问题，能成功连接broker，则会有类似以下的日志：

```powershell
 -------------- celery@Matrix.local v3.1.26.post2 (Cipater)
---- **** ----- 
--- * ***  * -- Darwin-17.5.0-x86_64-i386-64bit
-- * - **** --- 
- ** ---------- [config]
- ** ---------- .> app:         proj:0x108ab1eb8
- ** ---------- .> transport:   amqp://user:**@127.0.0.1:5672//
- ** ---------- .> results:     amqp://
- *** --- * --- .> concurrency: 4 (prefork)
-- ******* ---- 
--- ***** ----- [queues]
 -------------- .> celery           exchange=celery(direct) key=celery
                

[tasks]
  . demo.tasks.async_demo_task

[2018-04-24 08:24:47,656: INFO/MainProcess] Connected to amqp://user:**@127.0.0.1:5672//
```

需要注意的是日志中的tasks部分，可以看到已经自动识别到了demo.tasks.async_demo_task这个用于演示的任务。

如果没有识别到，检查下celery实例是否调用autodiscover_tasks方法，或配置文件的CELERY_IMPORTS是否配置正确。

### 调用异步任务

在demo/views.py中定义一个页面，只用来调用异步任务。

```python
from django.http import HttpResponse
from demo.tasks import async_demo_task

# Create your views here.
def demo_task(request):
	# delay表示将任务交给celery执行
    async_demo_task.delay()
    return HttpResponse('任务已经运行')
```

在proj/urls.py中注册对应的url。

```python
from django.contrib import admin
from django.urls import path
from demo.views import demo_task

urlpatterns = [
    path('admin/', admin.site.urls),
    path('async_demo_task', demo_task),
]
```

最后，启动django，访问url http://127.0.0.1:8000/async_demo_task 调用异步任务。

在worker的日志中，可以看到类似的执行结果，即说明任务已经由celery异步执行。

如果出现"Using settings.DEBUG leads to a memory leak, never "的警告信息，则在生产环境中关闭掉django的debug模式即可。

```powershell
[2018-04-24 09:25:52,677: INFO/MainProcess] Received task: demo.tasks.async_demo_task[1105c262-9371-4791-abd2-6f78d654b391]
[2018-04-24 09:25:52,681: INFO/Worker-4] run async_task
[2018-04-24 09:25:52,899: INFO/MainProcess] Task demo.tasks.async_demo_task[1105c262-9371-4791-abd2-6f78d654b391] succeeded in 0.21868160199665s: None
```

## 为任务分配队列

请参考另一个项目[celery-demo](https://github.com/blackmatrix7/celery-demo)

## 配置计划任务

同样请参考另一个项目[celery-demo](https://github.com/blackmatrix7/celery-demo)

## 使用Django Admin管理Celery计划任务

使用djcelery，而不直接使用celery的好处就在于可以通过Django Admin对Celery的计划任务进行管理。

### 创建数据库

`python manage.py migrate`

创建Django Admin和djcelery对应的表，这里的数据库使用默认的sqlite。

### 创建管理员

`python manage.py createsuperuser`，依次输入超级管理员帐号、邮箱、密码。

演示项目中设置帐号：admin  密码： superplayer123

### 修改配置文件

在settings.py中，增加两项配置：

```python
# 设定时区，配置计划任务时需要
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
```

### 创建计划任务

访问 http://127.0.0.1:8000/admin/djcelery/periodictask/add/，用于创建定时任务。

简单的解释下创建定时任务的选项：

| 字段               | 说明                                                 |
| ------------------ | ---------------------------------------------------- |
| 名称               | 便于理解的计划任务名称                               |
| Task (registered)  | 选择一个已注册的任务                                 |
| Task (custom)      |                                                      |
| Enabled            | 任务是否启用                                         |
| Interval           | 按某个时间间隔执行                                   |
| Crontab            | 定时任务， 和Interval二选一                          |
| Arguments          | 以list的形式传入参数，json格式                       |
| Keyword arguments: | 以dict的形式传入参数，json格式                       |
| Expires            | 任务到期时间                                         |
| Queue              | 指定队列，队列名需要在配置文件的 CELERY_QUEUES定义好 |
| Exchange           | Exchange                                             |
| Routing key        | Routing key                                          |

## 通过Model操作计划任务

本质上来说，就是对PeriodicTask这个model的操作。

下面模拟一个简单的增加计划任务的接口：

```python
def add_task(request):
    interval = IntervalSchedule.objects.filter(every=30, period='seconds').first()
    periodic_task = PeriodicTask(name='test', task='demo.tasks.async_demo_task', interval=interval)
    periodic_task.save()
    return HttpResponse('任务已经添加')
```

在proj/urls.py中增加url地址进行访问：

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('async_demo_task', demo_task),
    path('add_task', add_task),
    path('get_periodic_task_list', get_periodic_task_list),
]
```

通过浏览器访问http://127.0.0.1:8000/add_task 就可以直接添加一个间隔30秒的计划任务了。

再添加之前，请确保beat和worker正常运行，然后在beat中可以看到类似日志，检测到了Schedule改变，并且自动运行刚刚添加的任务。

```
[2018-05-03 17:18:10,012: INFO/MainProcess] DatabaseScheduler: Schedule changed.
[2018-05-03 17:18:10,013: INFO/MainProcess] Writing entries (0)...
[2018-05-03 17:18:40,020: INFO/MainProcess] Scheduler: Sending due task test (demo.tasks.async_demo_task)
[2018-05-03 17:19:10,021: INFO/MainProcess] Scheduler: Sending due task test (demo.tasks.async_demo_task)
```

同样的，通过获取PeriodicTask的数据，也可以得到正在运行的任务。

```python
def get_periodic_task_list(request):
    """
    获取周期性任务列表
    :return:
    """
    periodic_task_list = PeriodicTask.objects.all()
    data = [model_to_dict(periodic_task) for periodic_task in periodic_task_list]
    resp = json.dumps(data, cls=CustomJSONEncoder, ensure_ascii=False)
    return HttpResponse(resp, content_type='application/json', status=200)
```

更多的功能都可以通过操作djcelery的model进行实现。