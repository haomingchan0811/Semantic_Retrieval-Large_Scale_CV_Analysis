# -*- coding: utf-8 -*-
#!/usr/bin/python

import os
import string
import sys
import csv
import time
import opencc
import jieba
from numpy import *
from django.template.defaultfilters import last
reload(sys)
reload(string)
reload(os)
sys.setdefaultencoding('utf-8')

Link = {}

'''将职位经历id加入到字典'''
def storeIntoDict():
    reader = open('src/Prep_idAndpos.out', 'r')
    end = 0
    while not end:
        line = reader.readline()
        if line != '':
            id, pos = line.split('\x01', 1)
            Link[id] = pos
        else:
            end = 1

'''将字典内职位信息与job.csv的信息连接到一起'''
def linker():
    reader = open('src/job.csv', 'r')
    writer = open('src/all.info', 'w')
     
    i = 1
    stop = 0
    while not stop:
        line = reader.readline().replace('"','')
        if line == '':
            stop = 1
        else:
            index, cv_id, job_item, start, end, inc_id, inc_cn, ind_id, gender, dob, update = line.split(',', 10)
            if index == '':
                writer.write('' + '\x01')
                writer.write(cv_id + '\x01')
                writer.write(job_item + '\x01')
                writer.write('position' + '\x01')
                writer.write(start + '\x01')
                writer.write(end + '\x01')
                writer.write(inc_id + '\x01')
                writer.write(inc_cn + '\x01')
                writer.write(ind_id + '\x01')
                writer.write(gender + '\x01')
                writer.write(dob + '\x01')
                writer.write(update)
            else:
                if Link.has_key(job_item):
                    print i
                    writer.write('%d\x01' % i)
                    writer.write(cv_id + '\x01')
                    writer.write(job_item + '\x01')
                    writer.write('%s\x01' % Link[job_item].strip('\n'))
                    writer.write(start + '\x01')
                    writer.write(end + '\x01')
                    writer.write(inc_id + '\x01')
                    writer.write(inc_cn + '\x01')
                    writer.write(ind_id + '\x01')
                    writer.write(gender + '\x01')
                    writer.write(dob + '\x01')
                    writer.write(update)
                    i += 1

'''筛选出某个行业的条目'''           
def industryExtract(id):
    reader = open('src/all.info', 'r')
    writer = open('src/Ind_Internet.short', 'w')
#     writer = open('src/testWMD.txt', 'w')
     
    i = 1
    stop = 0
    while not stop:
        line = reader.readline()
        if line == '':
            stop = 1
        else:
            index, cv_id, job_item, pos, start, end, inc_id, inc_cn, ind_id, gender, dob, update = line.split('\x01', 11)
            if index == '':
                pass
#                 writer.write('' + '\x01')
#                 writer.write(cv_id + '\x01')
#                 writer.write(job_item + '\x01')
#                 writer.write(pos + '\x01')
#                 writer.write(start + '\x01')
#                 writer.write(end + '\x01')
#                 writer.write(inc_id + '\x01')
#                 writer.write(inc_cn + '\x01')
#                 writer.write(ind_id + '\x01')
#                 writer.write(gender + '\x01')
#                 writer.write(dob + '\x01')
#                 writer.write(update)
            else:
                '''互联网行业：ind_id为14'''
                if ind_id == str(id):
                    print i
#                     writer.write('%d\x01' % i)
#                     writer.write(cv_id + '\x01')
                    writer.write(job_item + '\x01')
                    writer.write(pos + '\x01')
                    writer.write(start + '\x01')
                    writer.write(end + '\n')
#                     writer.write(inc_id + '\x01')
#                     writer.write(inc_cn + '\x01')
#                     writer.write(ind_id + '\x01')
#                     writer.write(gender + '\x01')
#                     writer.write(dob + '\x01')
#                     writer.write(update)
                    i += 1
    
# storeIntoDict()
# linker()
industryExtract(14)
