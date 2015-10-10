# -*- coding: utf-8 -*-
#!/usr/bin/python

import os, string, sys, time
import jieba, math
# import opencc 
import WMD_Pos
from gensim import models
import numpy as np
import cPickle as pickle
import random
reload(sys)
reload(string)
reload(os)
sys.setdefaultencoding('utf-8')
# gc.set_debug(gc.DEBUG_LEAK) 

# model = models.word2vec.Word2Vec.load('word2vec_model/word2vec.model')

symbol = ['（', '）', '(',')','[',']','{','}','，',',', '、', '。','～',':','：', ';','?','/','^','`','@','＠',
                 '《', '》', '—', '；','!','！','"','“','”',"-", ',','\\','&','＆','－','|','\\\'','／','【','】',
                 '*','-','~','<','>','…','·','=',"或","和","以及","及","等",
                 ]
STD = {}                 #职位名标准库
similarJob = []         #存储使用word2vec聚类的相似职位
matchLib = {}         #匹配成功的职位名对,用于算法加速

'''清洗职位名，保留标点符号和停用词前的职位名'''
def clean(text):
    text = text.decode('utf-8').upper()
#     text = opencc.convert(text, config='zht2zhs.ini')
    newText = ''
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
    for wd in text:
        if wd == '\n':
            break
        else:
            newText += wd
    return newText

'''Inverse Document Frequency'''
def IDF():
    IDFdict = {}        # record the IDF of every word
    infile = open('src/Pos_frequency', 'r')
    outfile = open('src/IDF.out', 'w')
    end = 0
    while not end:
        line = infile.readline().strip('\n').encode('utf-8')
        if line != '':
            seg = jieba.cut(line)
            for i in seg:
                if i not in IDFdict.keys():
                    IDFdict[i] = 1
                else:
                    IDFdict[i] += 1
        else:
            end = 1
    
    Len = len(IDFdict)                                      #Total number of words
    for i in IDFdict.keys():
        IDFdict[i] = math.log(Len / IDFdict[i])     # IDF of each word
        outfile.write('%s %s\n' % (i, IDFdict[i]))

    data = open('src/IDF.pk', 'w')                     #serialize the IDF dictionary into pickle file
    pickle.dump(IDFdict, data)
    data.close()

'''与职位库中的词条子串完全匹配，并加入库中'''
def addToStd(x):
    if len(STD) == 0:
        STD[x] = []
    else:
        hasAdd = False
        for key in STD.keys():
            if key in x:
                STD[key].append(x.encode('utf-8'))
                hasAdd = True
        if hasAdd == False:
            STD[x] = []

'''对长度为length的职位名词条进行词频统计'''    
def frequency(length, threshold = 100, Eng = False):
    Fdict = {}
    end = 0
    infile = open('src/Prep_pos.out', 'r')
    while not end:
        line = infile.readline().strip('\n').encode('utf-8')
        if line != '':
            if Eng == False:
                if len(line.decode('utf-8')) == length:
                    print length, line
                    if not Fdict.has_key(line):
                        Fdict[line] = 1
                    else:
                        Fdict[line] += 1
            else:
                if line.replace(' ','').isalpha() and len(line) > 10:
                    print 'E', line
                    if not Fdict.has_key(line):
                        Fdict[line] = 1
                    else:
                        Fdict[line] += 1
        else:
            end = 1
    sort_dict = sorted(Fdict.iteritems(), key = lambda d:d[1], reverse = True)
    Filter(sort_dict, threshold)

'''根据词频降序排列，抛弃低于threshold的词条'''
def Filter(dictionary, threshold):
    count = 1
    for item in dictionary:
        job = item[0].encode('utf-8')
        num = item[1]
        if num > threshold:  # 筛选出现频次达到一定数量的条目
            addToStd(job)
        count += 1

'''根据完全匹配规则迭代生成职业名大类'''
def roughClassify():
    wordLen = 2
    while wordLen <= 10:
        frequency(wordLen)
        wordLen += 1
        print 'wordLen = %d' % wordLen
    frequency(0, 20, True)
#     sortPrinter()

'''根据职业大类的元素数量降序输出文件'''
def sortPrinter():
    output = open('src/rough_STD.out','w')
    sort_STD = sorted(STD.iteritems(), key = lambda d:len(d[1]), reverse = True)
    i = 1
    for item in sort_STD:
        print '%d 【%s】: ' % (i, item[0].encode('utf-8')),
        print ', '.join(STD[item[0]])
        output.write('%d 【%s】: ' % (i, item[0].encode('utf-8')))
        output.write(', '.join(STD[item[0]]) + '\n')
        i += 1
    
'''构造两个职位名的最长公共子序列'''
def LCSLength(m, n, x = None, y = None, c = None, b = None):
    for i in range(1, m):
        for j in range(1, n):
            if x[i - 1] == y[j - 1]:
                c[i][j] = c[i - 1][j - 1] + 1
                b[i][j] = 'equals'
            elif c[i - 1][j] >= c[i][j - 1]:
                c[i][j] = c[i - 1][j]
                b[i][j] = 'up'
            else:
                c[i][j] = c[i][j - 1]
                b[i][j] = 'left'
                
'''查找生成最长公共子序列'''
def GetLCS(i, j, x = None, b = None):
    if i == 0 and j == 0:
        return
    elif i > 0 and j > 0:
        if b[i][j] == 'equals':
            GetLCS(i - 1,j - 1, x, b)
    #         common.append(x[i - 1])
            global common
            common += x[i - 1]
        elif b[i][j] == 'left':
            GetLCS(i, j - 1, x, b)
        else:
            GetLCS(i - 1, j, x, b)
            
'''LCS: Longest common subsequence'''
def LCS(x, y):
    x = x.decode('utf-8')
    y = y.decode('utf-8')
    m = len(x) + 1
    n = len(y) + 1
    b = [[0 for i in range(n)] for j in range(m)]
    c = [[0 for i in range(n)] for j in range(m)]
    global common
    common = ''
    LCSLength(m, n, x, y, c, b)
    GetLCS(m - 1, n - 1, x, b)
    return common

'''对每个职业大类，用最长公共子序列进行二级分类(用｛｝表示)'''
def second_Level_Classify():
    subLen = 3           # 二级小类包含元素的最小数量(除类名外)
    for item in STD.keys():
        length = len(STD[item])
        if length > subLen:     #自底向上搜索二级小类
            cur_index = length - 4
            elementOfSubclass = 0       #归入到二级小类的元素个数（包括小类的key）
            while cur_index >= 0:
                pos1 = STD[item][cur_index]
                subDict = {}
                pos2_index = cur_index + 1
                '''用LCS顺序检索能归并到小类的元素'''
                while pos2_index < length - elementOfSubclass:
                    if isinstance(STD[item][pos2_index], str):
                        pos2 = STD[item][pos2_index]
                        if LCS(pos1, pos2) == pos1:
                            if not subDict.has_key(pos1):
                                subDict[pos1] = [pos2,]
                            else:
                                subDict[pos1].append(pos2)
                    pos2_index += 1
                    '''旧版本:二级小类放在所属的大类下面'''
#                 '''分为二级小类：删去大类中的相关元素，加入小类'''
#                 if subDict.has_key(pos1) and len(subDict[pos1]) >= subLen:
#                     for j in subDict[pos1]:
#                         STD[item].remove(j)
#                         elementOfSubclass += 1
#                     STD[item].remove(pos1)
#                     elementOfSubclass += 1
#                     STD[item].append(subDict)
#                 cur_index -= 1

                '''2015.8.5版本:将二级小类另存为大类,并在大类中,删去二级小类名,删去小类包含的元素'''
                if subDict.has_key(pos1) and len(subDict[pos1]) >= subLen:
                    if not STD.has_key(pos1):
                        STD[pos1] = []
                    for j in subDict[pos1]:
                        STD[pos1].append(j)
                        STD[item].remove(j)
                        elementOfSubclass += 1
                    STD[item].remove(pos1)
#                 STD[item].append(pos1) # 在大类中保留小类名,并放到类中最后
                    elementOfSubclass += 1
                cur_index -= 1
    Combine()
    Printer()

'''图操作类,包括点/边的建立以及深度优先搜索'''
class Graph(object):

    def __init__(self, *args, **kwargs):
        self.node_neighbors = {}
        self.visited = {}

    def add_node(self, node):
        if not node in self.nodes():
            self.node_neighbors[node] = []

    def add_edge(self, node1, node2):
        if(node1 not in self.node_neighbors[node2]) and (node2 not in self.node_neighbors[node1]):
            self.node_neighbors[node1].append(node2)
            self.node_neighbors[node2].append(node1)

    def nodes(self):
        return self.node_neighbors.keys()
        
    '''深度优先搜索DFS'''    
    def depth_first_search(self, root = None):
        def dfs(node):
            self.visited[node] = True
            w2v_similar.append(node)
            for n in self.node_neighbors[node]:
                if not n in self.visited:
                    dfs(n)
        if root:
            w2v_similar = []
            dfs(root)
            similarJob.append(w2v_similar)
        for node in self.nodes():
            if not node in self.visited:
                w2v_similar = []
                dfs(node)
                similarJob.append(w2v_similar)
                
'''将使用编辑距离无法聚类的相似职位使用word2vec合并到一类'''
def Combine():
    sort_STD = sorted(STD.iteritems(), key = lambda d:len(d[1]), reverse = True)
    '''对所有职位建立无向图,并将相似的职位建立边'''
    G = Graph()
    for job in sort_STD:
        G.add_node(job[0])
    for job1 in sort_STD:
        for job2 in sort_STD:
            if job1 != job2 and Similarity(job1[0], job2[0]) > 0.94:
#                 print job1[0].encode('utf-8'), job2[0].encode('utf-8')
                G.add_edge(job1[0], job2[0])
    '''遍历图进行深度优先搜索,将相似的职位合并(注意图中有多个子连通块)'''
    for job in sort_STD:
        G.depth_first_search(job[0])
    '''将相似的职位合并到一类中'''
    for simi in similarJob:
        if len(simi) > 1:
            name = ''                                             #合并后的大类名
            for job in simi:
                name += (job + '/')
            name = name[:-1]
            STD[name] = []                                    #合并后的新大类
            for job in simi:
                STD[name].append(job)                   # 添加合并职位名中的单个职位
                for subpos in STD[job]:
                    if subpos not in STD[name]:
                        STD[name].append(subpos)
#                 del STD[job]
            STD[name].sort()
    
'''两个职位的相似度'''
def Similarity(pos1, pos2, stdMatch = False):   #stdMatch表示是否在进行职位名到标准库的匹配
    if (not stdMatch) and Unlike(pos1, pos2):
        return 0
    word1 = wordVec(pos1)
    word2 = wordVec(pos2)
    '''两个职位向量的余弦距离(相似度) ,也可以替换成欧拉距离eulerDist()'''
    similarity = cosDist(word1, word2)
#     print pos1, pos2, similarity
    '''超过阀值则认为职位相似'''
    return similarity
    
'''基于word2vec模型的缺陷, 在合并职位名时, 规定的职位不相似的特殊规则'''
def Unlike(pos1, pos2):
    pos1 = pos1.encode('utf-8')
    pos2 = pos2.encode('utf-8')
    if pos1.replace(' ', '').isalpha() and pos2.replace(' ', '').isalpha():     #模型中任意英文的相似度都很高
        return True
    if ('工程师' in pos1 and pos1.rstrip('工程师').isalpha()) or ('工程师' in pos2 and pos2.rstrip('工程师').isalpha()):   #模型中PHP,ANDROID,JAVA等编程语言的相似度很高
        return True
    if not hasSameChar(pos1, pos2):
        return True
    return False
    
'''判断两个字符串是否含有相同的单字'''
def hasSameChar(x, y):
    x = x.decode('utf-8')
    y = y.decode('utf-8')
    judge = 0
    for i in x:
        if i in y:
            judge = 1
            break
    return judge

'''对职位进行分词,分隔符为空格;并将词向量加权合并为职位向量'''
def wordVec(text):
    seg = jieba.cut(text)
    vec = np.zeros(50,)     #职位向量初始化
    count = 0
    for i in seg:
        i = i.lower()
        if i in model.vocab:
            vec += model[i]
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

'''根据职业类别的元素数量降序输出文件'''
def Printer():
    NoOfClass = 0       #所有类别的数量
    output = open('src/STD.out','w')
    output2 = open('src/STD.lib','w')
    sort_STD = sorted(STD.iteritems(), key = lambda d:len(d[1]), reverse = True)
    i = 1
    for item in sort_STD:
        NoOfClass += 1
        print '%d 【%s】: ' % (i, item[0].encode('utf-8')),
        output.write('%d 【%s】: ' % (i, item[0].encode('utf-8')))
        output2.write('%s\n'% item[0].encode('utf-8'))
#         '''旧版本:二级小类放在所属的大类下面'''
#         for element in STD[item[0]]:
#             '''遇到字典类型元素，输出为二级小类'''
#             if isinstance(element, dict):
#                 NoOfClass += 1
#                 for subclass in element:
#                     print "\n%s  {%s}:" % (len(str(i)) * '  ', subclass.encode('utf-8')),
#                     print ', '.join(element[subclass]),
#                     output.write("\n%s {%s}:" % (len(str(i)) * ' ', subclass.encode('utf-8')))
#                     output.write(', '.join(element[subclass]))
#             else:
#                 print '%s, ' % element.encode('utf-8'),       
#                 output.write('%s, ' % element.encode('utf-8')) 
#         i += 1
 
        '''2015.8.5版本:将二级小类另存为大类,并在大类中,保留二级小类名,删去小类包含的元素'''
        for element in STD[item[0]]:
            print '%s, ' % element.encode('utf-8'),       
            output.write('%s, ' % element.encode('utf-8')) 
            output2.write('%s\n' % element.encode('utf-8')) 
        print '\n'
        output.write('\n\n') 
        i += 1
    print 'The total number of Categories is: %d' % NoOfClass

'''对于给定的职位名字，映射到标准库中的名字'''
def StdName(origin, data, Pos, X, Weight):
    '''2015.8.12版本:采用Word Mover Distance最小代价匹配'''
#     if origin in matchLib.keys():
#         std_name = matchLib[origin]
#     else:
    std_name = WMD_Pos.WMD_bt_queryAndLib(origin, Pos, X, Weight)
    candidates = Category(std_name, data)
    if len(candidates) == 1:
        std_name = candidates[0]
#             matchLib[origin] = std_name
    else:
        dist = 99999
        best_cand = ''
        for cand in candidates:
            d = WMD_Pos.WMD_bt_2texts(cand, origin)
            if d < dist:
                dist = d
                best_cand = cand
        std_name = best_cand
#     del candidates
#     gc.collect()
    return std_name 
    
    '''Old Version'''
#     inFile = open('STD.dict', 'r')           #反序列化出标准职位库
#     data = pickle.load(inFile)
#     origin = origin.upper()
#     candidate = set(['*'])       #与职位名标准库中匹配的备选名，*表示没有匹配的名字
#     for keys in data.keys():
#         Key = keys.split('/')
#         judge = 0   
#         for i in Key:           # 处理多相似职位的类
#             if i in origin or i == origin:
#                 judge = 1
#         if keys == origin or judge:
#             candidate.add(keys.decode('utf-8'))
#         for item in data[keys]:
#             if isinstance(item, dict):      #匹配则归入小类
#                 for i in item.keys():
#                     if i == origin or i in origin:
#                         candidate.append(i.decode('utf-8'))
#                     for sub in item[i]:
#                         if origin == sub or LCS(sub, origin) == sub: #sub in origin
#                             candidate.append(i.decode('utf-8'))
#             else:           #匹配则归入大类
#             if origin == item or LCS(item, origin) == item:        #item in origin
#                 candidate.add(keys.decode('utf-8'))
    '''旧版本:取匹配到的最长/详细的职位作为标准职位名'''
#     sort_cand = sorted(candidate, key = lambda d:len(d), reverse = True) 
#     std_name = sort_cand[0]
#     return std_name
    '''2015.8.7版本:采用word2vec模型的职位相似性匹配'''
#     std_name = ''
#     max_score = 0
#     for cand in candidate:
#         cand_score = Similarity(cand, origin, stdMatch = True)
# #         print origin, cand, cand_score
#         if cand_score > max_score:
#             max_score = cand_score
#             std_name = cand


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
    
    
'''抽取在某行业内进行过职位跳转更换的那些记录，并将职位名匹配到标准库中'''
def PosPath():
    WMD_Pos.std2vec()
    reader = open('src/PartOfPos/000', 'r')
    writer = open('src/Ind_Internet.path', 'a')         #!!!!!追加写文件参数为a
    inFile = open('src/STD.dict', 'r')           #反序列化出标准职位库
    data = pickle.load(inFile)
    with open('src/STDvectors.pk') as f:
        [Pos, X, Weight, words] = pickle.load(f)
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
    memRelease = 1      # 计算内存使用情况,用GC模块强制回收内存
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
    
def main():
    roughClassify()
    rough_time = time.clock()
    second_Level_Classify()
    subDivision_time = time.clock()
    data = open('src/STD.dict', 'w')       #将职位标准化字典序列化存入文件
    pickle.dump(STD, data)
    data.close()
    IDF()
    PosPath()
    map_time = time.clock()
    print 'Rough Classify: %s s\nSubdivision: %s s\nMapping To STD: %s s' % (rough_time, subDivision_time, map_time)

# main()
PosPath()



    
