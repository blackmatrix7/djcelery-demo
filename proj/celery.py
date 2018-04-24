#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2018/4/24 下午3:46
# @Author: BlackMatrix
# @Site: https://github.com/blackmatrix7
# @File: celery.py
# @Software: PyCharm
from celery import Celery
from django.conf import settings

__author__ = 'blackmatrix'

# 创建celery应用
celery_app = Celery('proj', broker=settings.CELERY_BROKER_URL)
# 从配置文件中加载除celery外的其他配置
celery_app.config_from_object('django.conf:settings')
# 自动检索每个app下的tasks.py
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
