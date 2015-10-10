# -*- coding: utf-8 -*-
#!/usr/bin/python

import os
import string
import sys
reload(sys)
reload(string)
reload(os)
sys.setdefaultencoding('utf-8')

'''统计裸职位的出现频次'''
def pos_freq():
    input = open('src/Prep_pos.out','r')
    output = open('src/Pos_frequency','w')  
    dict = {}
    end = 0
    while not end:
        line = input.readline().strip('\n').encode('utf-8')
        if line != '':
            if not dict.has_key(line):
                dict[line] = 1
            else:
                dict[line] += 1
        else:
            end = 1
    sort_dict = sorted(dict.iteritems(), key = lambda d:d[1], reverse = True)
    printer(sort_dict, output)
    
'''统计两字职位的出现频次'''
def pos_2word_freq():
    input = open('src/Prep_pos.out','r')
    output = open('src/Pos_2word_freq.direct','w')  
    dict = {}
    end = 0
    while not end:
        line = input.readline().strip('\n').encode('utf-8')
        if line != '':
            if len(line) == 6 and line.isalnum() == False:
                if not dict.has_key(line):
                    dict[line] = 1
                else:
                    dict[line] += 1
        else:
            end = 1
    sort_dict = sorted(dict.iteritems(), key = lambda d:d[1], reverse = True)
    printer(sort_dict, output)
    
'''统计分词最后一段职位的出现频次'''
def pos_2word_indt_freq():
    input = open('src/pos_2word.out','r')
    output = open('src/Pos_2word_freq.indirect','w')  
    dict = {}
    end = 0
    while not end:
        line = input.readline().strip('\n').encode('utf-8')
        if line != '':
            if len(line) == 6 and line.isalnum() == False:
                if not dict.has_key(line):
                    dict[line] = 1
                else:
                    dict[line] += 1
        else:
            end = 1
    sort_dict = sorted(dict.iteritems(), key = lambda d:d[1], reverse = True)
    printer(sort_dict, output)

'''按频次大小降序排列'''
def printer(dictionary, out_file):
    # for k, v in dict.iteritems():
    # print "Key:  %s, Count:  %s" % (k,v)
    count = 1
    for item in dictionary:
        job = item[0].encode('utf-8')
        num = item[1]
        print count, job, num
        if num >= 500:  # 筛选出现频次达到一定数量的条目
            out_file.write('%s %d\n' % (job, num))
#             out_file.write(job+'\n')
            count += 1

pos_2word_indt_freq()
# pos_freq()