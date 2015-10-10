# -*- coding: utf-8 -*-
#!/usr/bin/python
'''Edited and Annotated by Haoming@iPIN on August, 2015'''

import os, sys, pickle
import numpy as np
import get_WMD_vectors, get_wmdDist
sys.path.append('WMD_code/python-emd-master')
sys.path.append('new_word')
from emd import emd
from word_cut import jieba
reload(sys)
sys.setdefaultencoding('utf-8')

'''加载word2vec c format 文件'''
def load_word_vector(vector_file,input_dim=200):
    file_dims = input_dim + 1
    word2vec_dict = {}
    with open(vector_file) as f:
        for i in f.readlines():
            i = i.strip()
            items = i.split(' ')
            if len(items) != file_dims: continue
            word2vec_dict[items[0]] = np.array(tuple(map(lambda x:float(x),items[1:])),dtype="float32")
    return word2vec_dict

def load_vector_file(vector_file):
    dims = -1
    word2vec_dict = {}
    with open(vector_file) as f:
        first_line = f.readline()
        first_line = first_line.strip()
        line_num,dims = first_line.split()
    dims = int(dims)
    if dims == -1: return word2vec_dict
    return dims,load_word_vector(vector_file, input_dim = dims)

'''寻找一个标准职位名在库中所属的类别名(可能有多个match)'''
def Category(origin, data):
    origin = origin.upper()
    candidate = []
    for Keys in data.keys():
        if Keys == origin:
            candidate.append(Keys)
        else:
            for pos in data[Keys]:
                if pos == origin:
                    candidate.append(Keys)
    return candidate

'''对于给定的职位名字，映射到标准库中的名字'''
def StdName(origin, data, Pos, X, Weight):
    '''2015.8.12版本:采用Word Mover Distance最小代价匹配'''
#     if origin in matchLib.keys():
#         std_name = matchLib[origin]
#     else:
    std_name = get_wmdDist.WMD_bt_queryAndLib(origin, Pos, X, Weight, vec_size, model)
    candidates = Category(std_name, data)
    if len(candidates) == 1:
        std_name = candidates[0]
#             matchLib[origin] = std_name
    else:
        dist = 99999
        best_cand = ''
        for cand in candidates:
            d = get_wmdDist.WMD_bt_2texts(cand, origin, vec_size, model)
            if d < dist:
                dist = d
                best_cand = cand
        std_name = best_cand
    return std_name 
    
'''抽取在某行业内进行过职位跳转更换的那些记录，并将职位名匹配到标准库中'''
def PosPath():
    get_WMD_vectors.pos2vec()
    print 'done!'
    reader = open('../src/PartOfPos/000', 'r')
    writer = open('Ind_Internet.path', 'a')         #!!!!!追加写文件参数为a
    inFile = open('../src/STD.dict', 'r')           #反序列化出标准职位库
    data = pickle.load(inFile)
    with open('wmdVectors.pk') as f:
        [Pos, X, Weight] = pickle.load(f)
#     noMatch = []
    Path = {}
    count = 0    #记录有效的职位跳转数量（以个人为单位)
    stop = 0
    c = 1
    rc = 1
    while not stop:
        line = reader.readline()
        if line == '':
            stop = 1
        else:
            cv_id, job_item, pos, start, end = line.split('\x01', 4)
#             pos = opencc.convert(pos, config = 'zht2zhs.ini')
            c += 1
            if not Path.has_key(cv_id):
                Path[cv_id] = [{"Job_item": job_item, "Pos":pos, "Start":start, "End":end},]
            else:
                Path[cv_id].append({"Job_item": job_item, "Pos":pos, "Start":start, "End":end})
    print 'Load complete: %d job records' % c
#     memRelease = 1      # 计算内存使用情况,用GC模块强制回收内存
#     print'====================================='
#     objgraph.show_growth()
    for cv in Path.keys():
#         print'====================================='
#         objgraph.show_growth()      
#         objgraph.show_chain(objgraph.find_backref_chain(random.choice(objgraph.by_type('list')),objgraph.is_proper_module),filename='chain.png')
#         objgraph.show_backrefs([x], filename='sample-backref-graph.png')
        validRecord = 0
        prev_job = ''
        sort_P = sorted(Path[cv], key = lambda d:d['Job_item'], reverse = True)
        '''选出有效跳转经历大于１的那些条目'''
        for job in sort_P:
            print '%d out of %d records' % (rc, c)          # 已经遍历的职位记录数目
            rc += 1
            #筛掉混乱的过长描述(英文除外)及实习/兼职经历，标识符为xxx:9999或xxx:10000
            if len(job['Job_item']) < 29 and job['Pos'] != prev_job: 
                if len(job['Pos'].decode('utf-8')) <= 10 or job['Pos'].replace(' ','').isalpha():
                    validRecord += 1
                    prev_job = job['Pos']
        if validRecord > 1:
            count += 1
            prev_job = ''
            print '----------------------------------------------------------'
            print '%d' % count
            for i in sort_P:
                if len(i['Job_item']) < 29 and i['Pos'] != prev_job:                                                                                                                                                                                                                                                                                                                                                                                 
                    if (len(i['Pos'].decode('utf-8')) <= 14 or i['Pos'].replace(' ','').isalpha()):
#                         memRelease += 1
#                         print 'memRelease = %d' % memRelease
    #                     position = clean(i['Pos'])
                        stdPos = StdName(i['Pos'], data, Pos, X, Weight)   
    #                     if stdPos == '*':
    #                         noMatch.append(i['Pos'].encode('utf-8'))
                        writer.write(i['Job_item'] + '\x01')
                        writer.write(i['Pos'] + '\x01')
                        writer.write(stdPos + '\n')      #将职位名替换为标准库中的名字 
                        print i['Pos'], '-->', stdPos
                        prev_job = i['Pos']
            writer.write('\n')
#     print "The following jobs can't find a match in the standard position database:"
#     for j in noMatch:
#         print j
#     print len(noMatch)

if __name__ == '__main__':
    [vec_size, model] = load_vector_file('word2vec_new_word.model')
    PosPath()