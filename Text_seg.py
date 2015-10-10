# -*- coding: utf-8 -*-
#!/usr/bin/python

import os
import sys
import string
import jieba
reload(string)
reload(os)
reload(sys)
sys.setdefaultencoding('utf-8')

stopwords = set(["-","、","，", "(",")","+","？","—","！","】","【","·"," ",",","（","）","~","!","．","<",":",".","\"","•",">","《","》","/","//", "。" , "1","2","3","4","5","6","7","8","9","0", "10","11", 
                            "负责","根据","通过","参与","解决","相关","进行","利用","能够","自己","跟","以及","和","工作","一个","主要","公司","一定","日常","其他","其它"])

'''对每一行的职位名进行分词'''
def pos_seg():
    in_file = open('src/Prep_pos.out','r')
    out = open('src/Prep_pos_seg.out', 'w') 
    end = 0
    count = 1
    while not end:
        line = in_file.readline()
        if line != '':
            line = line.strip()
            seg = jieba.cut(line)
            for i in seg:
                out.write(i.encode('utf-8') + ' ')
                print i.encode('utf-8')
            out.write('\n')
            print count
            count = count + 1
        else:
            end = 1
    in_file.close()
    print "*******Complete!*******"

'''对每一行的职位描述进行分词'''
def despt_seg():
    in_file = open('Prep_desciption.out','r')
    out = open('Prep_despt_seg.out', 'w') 
    end = 0
    count = 1
    while not end:
        line = in_file.readline()
        if line != '':
            line = line.strip()
            seg = jieba.cut(line)
            for i in seg:
                out.write(i.encode('utf-8') + ' ')
                print i.encode('utf-8')
            out.write('\n')
            print count
            count = count + 1
        else:
            end = 1
    in_file.close()
    print "*******Complete!*******"

'''对每一行的职位名进行分词，并只保留最后一段分词（General的职位名）'''
def general_pos_seg():
    in_file = open('src/Prep_pos.out','r')
    out = open('src/pos_2word.out', 'w') 
    end = 0
    count = 1
    while not end:
        line = in_file.readline()
        if line != '':
            line = line.strip()
            seg = jieba.cut(line)
            for i in seg:
                general = i.decode('utf-8')
            if len(general) == 2:
                out.write(general + '\n') 
                print count, general
                count = count + 1
        else:
            end = 1
    in_file.close()
    print "*******Complete!*******"

# general_pos_seg()
# pos_seg()
despt_seg()

