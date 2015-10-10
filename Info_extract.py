# -*- coding: utf-8 -*-
#!/usr/bin/python

''' 提取并预处理raw文件夹中的职位名称属性，所在源文件及在文件中出现的行数 '''
import os
import sys
import string
import opencc
reload(string)
reload(os)
reload(sys)
sys.setdefaultencoding('utf-8')

''' 非法描述，如职位为：\N/ 空 / 无 '''
illegal = ['\N','N', '', '无','空','暂无']

symbol = ['（', '）', '(',')','[',']','{','}','，',',', '、', '。','～',':','：', ';','?','/','^','`','@','＠',
                 '《', '》', '—', '；','!','！','"','“','”',"-", ',','\\','&','＆','－','|','\\\'','／','【','】',
                 '*','-','~','<','>','…','·','=',"或","和","及","以及","等等",
                 ]
Number = ['一','二','三','四','五','六','七','八','九','十','十一','十二']

'''判断职位中是否出现了symbol中的字符'''
def hasSymbol(text):
    judge = 0
    for sym in symbol:
        if sym in text:
            judge = 1
            break
    if '兼' in text and '兼职' not in text:
        judge = 1
    if '+' in text and 'C++' not in text:
        judge = 1
    if '＋' in text and 'C＋＋' not in text:
        judge = 1
    if '#' in text and 'C#' not in text:
        judge = 1
    if '＃' in text and 'C＃' not in text:
        judge = 1
    if '.' in text and '.NET' not in text:
        judge = 1
    if ' ' in text and not text.replace(' ', '').isalpha():
        judge = 1
    return judge

''' 去掉职位中的所有标点符号和空格，另起生成新的职位名'''
def clean(text):
#     delset = string.punctuation + string.digits + ' '
#     text = text.translate(None, delset)
    text = text.upper()
    text = opencc.convert(text, config='zht2zhs.ini')   #繁体转化为简体
    for i in symbol :
        text = text.replace(i, '\n')
    if '兼' in text and '兼职' not in text:
        text = text.replace('兼', '\n')
    if '+' in text and 'C++' not in text:
        text = text.replace('+', '\n')
    if '＋' in text and 'C＋＋' not in text:
        text = text.replace('＋', '\n')
    if '#' in text and 'C#' not in text:
        text = text.replace('#', '\n')
    if '＃' in text and 'C＃' not in text:
        text = text.replace('＃', '\n')
    if '.' in text and '.NET' not in text:
        text = text.replace('.', '\n')
    if ' ' in text and not text.replace(' ', '').isalnum():
        text = text.replace(' ', '\n')
    return text

def sentence(text):
    for i in symbol:
        text = text.replace(i, '')
    if '兼' in text and '兼职' not in text:
        text = text.replace('兼', '')
    text = text.upper()
    for i in range(1, 20):
        text = text.replace(i, '\n')
    for i in Number:
        text = text.replace(i, '\n')
    return text

''' 从多个源文件中提取出职位数据 '''
def pos_extract():
    path = '/home/haoming/iPIN/haoming_position_all_14/raw/'
    file_list = os.listdir(path)
    output = open('src/Prep_pos.out','w')
    # outfile = open('File_name.out','w')
    count = 1
    
    for cur_file in file_list:
        if "crc" in cur_file:
            continue
        else:
            file_name = os.path.join(path, cur_file)
    #         outfile.write(file_name+'\n')
            f = open(file_name, 'r')
            end = 0
            while not end:
                line = f.readline()
                if line != '':
                    job_item, position, description = line.split('\x01', 2)
                    '''旧版本：对于每一个职位名，遇到停用词或标点符号则换行存取为新的职位名'''
#                     position = clean(position)                #
#                     if not position.replace(' ', '').isalpha():
#                         position.strip(' ')
#                     for item in position.split('\n'):
#                         if item not in illegal and item.isdigit() == False:
#                             output.write(item.encode('utf8') + '\n')
#                             count =  count + 1  
#                             print count,  item
                    '''2015.8.3修改版本：遇到停用词或标点符号抛弃该职位名（英语职位名中出现空格除外）'''
                    position = position.upper()                                                      #英文全部转为大写
                    position = opencc.convert(position, config = 'zht2zhs.ini')     #繁体转为简体
                    if (position not in illegal) and (not hasSymbol(position.encode('utf-8'))): # and (position.isdigit() == False) 
                        output.write(position.encode('utf8') + '\n')
                        count =  count + 1  
                        print count,  position
                else:
                    end = 1
        line = f.readline()
    f.close()
    print "*******Complete!*******"
    
'''从多个源文件中提取出职位名称和描述，用于主题模型训练 '''
def despt_extract():
    path = '/home/haoming/iPIN/haoming_position_all_14/raw/'
    file_list = os.listdir(path)
    output = open('Prep_desciption.out','w')
    # outfile = open('File_name.out','w')
    count = 1
    
    for cur_file in file_list:
        if "crc" in cur_file:
            continue
        else:
            file_name = os.path.join(path, cur_file)
    #         outfile.write(file_name+'\n')
            f = open(file_name, 'r')
            end = 0
            while not end:
                line = f.readline()
                if line != '':
                    job_item, position, description = line.split('\x01', 2)
                    description = clean(description)
                    description.strip(None)
                    for item in description.split('\n'):
                        if item not in illegal and item.replace(' ', '').isalnum()== False:
                            output.write(item + '\n')
                            count =  count + 1  
                            print count,  item
                else:
                    end = 1
        line = f.readline()
    f.close()
    print "*******Complete!*******"    


def data_extract():
    path = '/home/haoming/iPIN/haoming_position_all_14/raw/'
    file_list = os.listdir(path)
#     output = open('Prep_data.out','w')
    output = open('src/Prep_idAndpos.out','w')
#     outfile = open('File_name.out','w')
    count = 1
    
    for cur_file in file_list:
        if "crc" in cur_file:
            continue
        else:
            file_name = os.path.join(path, cur_file)
#             print file_name
#             outfile.write(file_name+'\n')
            f = open(file_name, 'r')
            i = 1
            end = 0
            while not end:
                line = f.readline()
                if(line !=''):
                    job_item, position, description = line.split('\x01', 2)
                    if position not in illegal:
#                         output.write(job_item + '\x01')
#                         output.write(position + '\n')
                        output.write('<id>' + job_item + '</id>\n')
                        output.write('<pos>' + position + '</pos>\n')
                        output.write(description)
                        count =  count + 1  
                        print count,  position
    #                     output.write('%10d  ' %count)
                        print ("%s  %s  %d\n" %(position, cur_file, i))
    #                     description = clean(description)
                    i += 1
                else:
                    end = 1
        line = f.readline()
    f.close()
    print "*******Complete!*******"


pos_extract()
# data_extract()
# despt_extract()

