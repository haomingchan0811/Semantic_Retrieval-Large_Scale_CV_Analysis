# -*- coding: utf-8 -*-
#!usr/bin/python
import os, sys, string, csv, time, opencc, matplotlib
import jieba
import math
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from gensim import models 
reload(sys)
reload(string)
reload(os)
sys.setdefaultencoding('utf-8')

G = nx.DiGraph()    
PosRank = {}         #记录职位的评级
maxRank = -1        #记录Page Rank计算结果的最小值
minRank = 9999    #记录Page Rank计算结果的最小值
count = 0
noOfLevel = 40      #职级数量

wd = models.word2vec.Word2Vec.load('word2vec_model/word2vec.model')        #导入word2vec模型
'''根据职位跳转记录建立有向图'''
def genGraph():
    infile = open('src/Ind_Internet.path', 'r')
    endOfRecord = 1     #是否为个人职业跳转记录的结尾
    lastJob = ''
#     testCase = 50
    for line in infile.readlines():
#         if testCase > 0:
        if line == '\n':
            endOfRecord = 1
        else:
            job_id, origin, stdName = line.split('\x01', 2)
#             stdName = opencc.convert(stdName, config='zht2zhs.ini')
            curJob = stdName.strip('\n')
            if curJob == '*':       #删去无法在职位标准库中匹配的职位记录
                continue
            else:    
                if not G.has_node(curJob):
                    G.add_node(curJob)
                if not endOfRecord and not G.has_edge(lastJob, curJob):     #TODO：可以考虑忽略跳转前相同的其中一条职位记录
                    '''判断职位跳转是否在合理接受范围内'''
                    if acceptable(lastJob.lower(), curJob.lower()):
                         G.add_edge(lastJob, curJob)
                endOfRecord = 0
                lastJob = curJob
#             testCase -= 1

'''判断职位跳转幅度是否在合理接受范围内'''
def acceptable(pos1, pos2):
    word1 = wordVec(pos1)
    word2 = wordVec(pos2)
    '''两个职位向量的余弦距离(相似度) ,也可以替换成欧拉距离eulerDist()'''
    similarity = cosDist(word1, word2)
    print pos1, pos2, similarity
    '''超过阀值则归为合理的跳转'''
#     if similarity > 0.1:    
#         return True
#     else:
#         return False
    return True

'''对职位进行分词,分隔符为空格;并将词向量加权合并为职位向量'''
def wordVec(text):
    seg = jieba.cut(text)
    vec = np.zeros(50,)     #职位向量初始化
    count = 0
    for i in seg:
        if i in wd.vocab:
            vec += wd[i]
            count += 1
        else:
            print '**', i
    if count != 0:
        vec /= count
    return vec

'''计算两个向量之间的余弦相似度'''
def cosDist(a, b):
    if len(a) != len(b):
        return None
    dividend = 0.0      #余弦公式的分子
    a_sq = 0.0             
    b_sq = 0.0
    for a1, b1 in zip(a,b):
        dividend += a1 * b1
        a_sq += a1 ** 2
        b_sq += b1 ** 2
    divisor = math.sqrt(a_sq * b_sq)      #余弦公式的分母
    if divisor == 0.0:
        return None
    else:
        return dividend / divisor

'''计算两个向量之间的欧拉距离'''
def eulerDist(a, b):
    if len(a) != len(b):
        return None
    dist = 0.0
    for a1, b1 in zip(a,b):
        dist += (a1 - b1) ** 2
    return dist
        
'''利用Page Rank算法对所有职位进行评级（1～20）'''
def PageRank():    
    global count, maxRank, minRank, noOfLevel
    pr = nx.pagerank(G, 0.85)
    for node in pr.keys():
        if not PosRank.has_key(node):
            count += 1
            PosRank[node] = [pr[node]]
#             print PosRank[node][0]
#             print node, pr[node]
            if maxRank < pr[node]:
                maxRank = pr[node]
            if minRank > pr[node]:
                minRank = pr[node]
    for node in PosRank.keys():
        PosRank[node].append(int((noOfLevel - 1) * (PosRank[node][0] - minRank) / (maxRank - minRank)) + 1)

#     plt.figure('Position Rank')
#     layout = nx.spring_layout(G)
#     nx.draw(G, pos = layout, node_size=[x * 500 for x in pr.values()], node_color = 'r', with_labels = True, fontproperties = myfont)
#     plt.show()

'''将职位与其评级降序输出，并存入csv文件'''
def rankPrinter():
    rank_count = {}      #改进的类幂方分布
    rank_count1 = {}    #等区间分布 
    for i in range(1, noOfLevel + 1):
        rank_count[i] = 0   
        rank_count1[i] = 0
    outfile = open('src/PosRank.csv', 'w')
    w = csv.writer(outfile, dialect = 'excel')
    w.writerow(['职位名', 'Page Rank得分', '类幂方分布', '等区间分布'])
    sortRank = sorted(PosRank.iteritems(), key = lambda d: d[1][0], reverse = True)
    level = 10
    levelCount = 0
    temp = 12.2          # small trick to ensure the ideal rank distribution
    '''改进的幂方职级分布'''
    for job in sortRank:
        if levelCount < pow(2, temp - level):
            levelCount += 1
        elif level == 1:
            levelCount += 1
        else:
            level -= 1
            if level % 2 == 0:
                temp -= 1
            levelCount = 1
        w.writerow([job[0].encode('utf-8'), job[1][0], level, job[1][1]])
        rank_count[level] += 1            
        rank_count1[job[1][1]] += 1      
    print '[Squared Distribution]'
    for i in reversed(range(1, 11)):
        print 'Level %d: %d' % (i, rank_count[i])
    print '\n[Equi-Interval Distribution]'
    for i in reversed(range(1, noOfLevel+ 1)):
        print 'Level %d: %d' % (i, rank_count1[i])
        
def main():
    t = time.clock()
    genGraph()
    print 'DiGraph Generation Complete: %ss' % t
    PageRank()
    rankPrinter()
    print '\nMaximum Rank = %s' % maxRank
    print 'Minimum Rank = %s' % minRank
    print 'No. of Position = %s' % count
    
main()
# while True:
#     a = raw_input()
#     b = raw_input()
#     print acceptable(a, b)