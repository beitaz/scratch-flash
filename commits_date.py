#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 注意： 必须在本地 Git 项目下运行此脚本
# pylint: disable=C0111,C0103,C0410,W0311
import os, re, subprocess
from dateutil.parser import parse

# 获取当前项目名称： scratch-blocks  =>  prefix = 'blocks'
# prefix = os.getcwd().split('/')[-1].split('-')[-1]
# user_home = os.path.join(os.path.expanduser('~'))
origin_filename = os.path.join(os.getcwd(), 'all-temp-commits.log')
target_filename = os.path.join(os.getcwd(), 'all-commits.log')

# 将正则匹配结果转换为指定格式的字符串
def local_time(time_str):
  local_timestamp = parse(time_str.group())
  print local_timestamp
  local = local_timestamp.strftime("%Y-%m-%d %H:%M:%S")
  return local + '    '

# 删除已存在的原始 git log 文件
if os.path.exists(origin_filename):
  os.remove(origin_filename)

# shell 执行 git log >> file_name 生成原始 git log 文件
process = subprocess.call("git log --pretty=format:'%%H    %%cd    %%s' >> %s" % origin_filename,
                          shell=True)

# 正则表达式格式化日期，并写入新文件
if process == 0:
  print 'SUCCESS.'
  origin_file = open(origin_filename, 'r')
  target_file = open(target_filename, 'w+')
  for line in origin_file.readlines():
    new_line = re.sub(r'\w{3}\s\w{3}.*[-+]\d{4}\s{4}', local_time, line)
    target_file.write(new_line)

  origin_file.close()
  target_file.close()
  os.remove(origin_filename)
