#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2018/4/24 下午3:58
# @Author: BlackMatrix
# @Site: https://github.com/blackmatrix7
# @File: tasks.py
# @Software: PyCharm
import logging
from proj.celery import celery_app
__author__ = 'blackmatrix'


@celery_app.task
def async_demo_task():
    logging.info('run async_task')


if __name__ == '__main__':
    pass
