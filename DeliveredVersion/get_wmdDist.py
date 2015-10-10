# -*- coding: utf-8 -*-
#!/usr/bin/python
'''Edited and Annotated by Haoming@iPIN on August, 2015'''

import os, gensim, sys, pickle, csv, math
import numpy as np
from numpy import vstack
sys.path.append('WMD_code/python-emd-master')
from emd import emd
sys.path.append('new_word')
from word_cut import jieba
# import jieba
reload(sys)
sys.setdefaultencoding('utf-8')

# model = gensim.models.word2vec.Word2Vec.load('word2vec_new_word.model') # load word2vec model
IDF = 'IDF.pk'      # absolute file path of IDF stored offline

symbol = ['（', '）', '(',')','[',']','{','}','，',',', '、', '。','～',':','：', ';','?','/','^','`','@','＠',
                 '《', '》', '—', '；','!','！','"','“','”',"-", ',','\\','&','＆','－','|','\\\'','／','【','】',
                 '*','-','~','<','>','…','·','=',"或","和","以及","及","等",
                 ]

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
            continue
        else:
            newText += wd
    return newText

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

# [vec_size, model] = load_vector_file('word2vec_new_word.model')

''' given a text, return its segmentation with blank space in-between '''
def segmentation(text):
    newText = ''
    text = text.strip()
#     text = text.translate(string.maketrans("",""), string.punctuation)      # remove the punctuation
    seg = jieba.cut(text)
    for wd in seg:
        newText += wd
        newText += ' '
    return newText.strip()

''' calculate the vectors of words (including the w2v vectors as well as the weight vectors) '''
def generateVec(W):
    # store each word's vector in a column
    F = np.zeros((vec_size, len(W)))
    # store the split words in order: repeated word will be stored in its first occurrence and then stored as '' afterwards
    word_order = np.zeros((len(W)), dtype=np.object)  
    inner = 0                                                    # iterator for the split words
    idf_set = pickle.load(open(IDF))                 # IDF stored offline
    bow_x = np.zeros((len(W),))                      # BOW vector: occurrence of each word in the word_order matrix
    idf_x = np.zeros((len(W),))                         # IDF of each non-repeat word
    for word in W[0 : len(W)]:                   
        word = word.encode('utf-8')
        try:
            test = model[word]                  # w2v embedding word vector
            if word in word_order:
                IXW = np.where(word_order==word)
                bow_x[IXW] += 1                 # occurrence of the repeated word recorded at its first occurred position
                word_order[inner] = ''          # repeated word will be stored as '' for the 2nd or later occurrence 
            else:
                word_order[inner] = word    # store the word at its first occurrence
                bow_x[inner] += 1                # number of occurrence of the word 
                if idf_set.has_key(word):       # IDF of the word
                    idf_x[inner] = idf_set[word]    
                else:
                    idf_x[inner] = 1.38            # if IDF does not exist, the word will be given a rather small weight (Reference: IDF(经理) = 1.38629436112)                  
                F[:,inner] = test                     # load the corresponding w2v word vector into the corresponding column 
        except KeyError, e:
            print "KeyError"
            word_order[inner] = ''
        inner = inner + 1
        
    bow_xs = bow_x[bow_x != 0]                              # remove the 0s(representing repeated words)
    idf_xs =  idf_x[idf_x != 0]                                     # remove the 0s(representing repeated words)
    Fs = F.T[~np.all(F.T == 0, axis=1)]                      # F.T: transpose of the F matrix; '~': converse position logical(按位取反);
    bow_i = bow_xs                                                   # the BOW vector matrix of the document
    bow_i = bow_i / np.sum(bow_i)                            # calculate the frequency of each word in the document
    bow_xs = bow_i                            
    idf_xs = idf_xs / np.sum(idf_xs)                             # normalize the IDF 
#     weight = idf_xs                                     # Total weight combing the BOW weight and IDF
    weight = bow_xs + idf_xs                                     # Total weight combing the BOW weight and IDF
    return (Fs, weight)

''' calculate the WMD distance between query and each job title in Library '''
def WMD_bt_queryAndLib(query, Pos, X, Weight_X):
# X:w2v vectors matrix, iTH column is the iTH document's w2v vectors matrix (list type)
# Weight_X: weight vectors matrix, iTH column is the iTH document's TF vectors matrix (list type)
    n = np.shape(X)
    n = n[0]                                                  # number of documents 
    Dist = []
    query = clean(query)
    (Fs, weight) = generateVec(segmentation(query.lower()).split())
    query_weightVec = weight.tolist()          # weight word vector of query
    query_w2vVec = Fs.T.T.tolist()                # w2v word vector of query
    for j in xrange(n):
        emdDist = emd((query_w2vVec, query_weightVec), (X[j].T.tolist(), Weight_X[j].tolist()), distance)
        if math.isnan(emdDist):                     # NOTICE! this sentence used to be missing and triggered a bug
            emdDist = 9999
#         Dist.append(emdDist)                        # calculate the EMD of two documents
        Dist.append((Pos[j], emdDist))     # calculate the EMD of two documents
    sort_Dist = sorted(Dist, key = lambda d: d[1])
    print '-----------------------------------------------'
    if len(sort_Dist) >= 5:
        for i in range(5):
            print '%f    %s' % (sort_Dist[i][1], sort_Dist[i][0].encode('utf-8'))
    else:
        for i in range(len(sort_Dist)):
            print '%f    %s' % (sort_Dist[i][1], sort_Dist[i][0].encode('utf-8'))
#     return sort_Dist[0][0]
    return sort_Dist
#     return Dist                                               # return a list of Word Mover Distance

''' calculate the WMD distance between two texts '''
def WMD_bt_2texts(text1, text2):
    (Fs, weight) = generateVec(segmentation(text1.lower()).split())
    text1_BOWVec = weight.tolist()               # BOW word vector of text
    text1_w2vVec = Fs.T.T.tolist()                   # w2v word vector of text
    (Fs, weight) = generateVec(segmentation(text2.lower()).split())
    text2_BOWVec = weight.tolist()               # BOW word vector of text
    text2_w2vVec = Fs.T.T.tolist()                   # w2v word vector of text
    Dist = emd((text1_w2vVec, text1_BOWVec), (text2_w2vVec, text2_BOWVec), distance)   # calculate the EMD of two documents
    if math.isnan(Dist):
        Dist = 9999
    return Dist

''' Euclidian distance between two word vectors '''
def distance(x1, x2):                                
    return np.sqrt(np.sum((np.array(x1) - np.array(x2)) ** 2))

''' A matrix containing WMD between each other job-titles '''
def WMD_bt_EachOther_inLib(Pos, X, Weight_X):
    n = np.shape(X)
    n = n[0]                                                      # number of documents 
#     wmdDist = np.zeros((n, n))                        # WMD matrix: WMD between each job titles
    infile = open('STD.lib', 'r')
    i = 0
    for line in infile:
        print '%d out of %d: %s' % (i, n, line.strip())
        if i == 0:
            wmdDist = WMD_bt_queryAndLib(line.strip(), Pos, X, Weight_X)
        else: 
            wmdDist = vstack((wmdDist, WMD_bt_queryAndLib(line.strip(), Pos, X, Weight_X)))
        i += 1
    print wmdDist
    with open('wmdDist.pk', 'w') as f:
        pickle.dump([Pos, wmdDist], f)
        f.close()
        
''' Given a list of raw job titles, for each job title, return the top K similar position-directions '''
def pos_Direction_Projection():
    infile = open('../src/rawPos', 'r')
    outfile = open('PosDirection_Projection_Top10.pk', 'w')
#     Projection = csv.writer(outfile)
#     Projection.writerow(['Position', '1st Direction', '2nd Direction', '3rd Direction'])
    Projection = {}     # store the top 10 projections of each raw position and the corresponding similarity values 
    for line in infile.readlines():
        if line != '':
            line = line.strip().encode('utf-8')
            print line
            if not Projection.has_key(line):
                Projection[line] = {}
            dict = WMD_bt_queryAndLib(clean(line), Pos, X, Weight_X)
            for i in xrange(10):
                category = dict[i][0].encode('utf-8')
                similarity = dict[i][1]
                Projection[line][category] = similarity
#             Projection.writerow(result)
    pickle.dump(Projection, outfile)
    outfile.close()
    
''' Given a list of position-directions, for each direction, return the top K similar job titles'''
def most_Similar_Member():
    infile = open('../src/Pos_direction', 'r')
    outfile = open('rawPos_Projection.csv', 'w')
    Projection = csv.writer(outfile)
    Projection.writerow(['Pos Direction', '1st pos', '2nd pos', '3rd pos'])
    for line in infile.readlines():
        if line != '':
            line = line.strip()
            print line
            dict = WMD_bt_queryAndLib(clean(line), Pos, X, Weight_X)
            result = [line]
            for i in xrange(3):
                temp = dict[i][0].decode('utf8')
                result.append(temp)
            Projection.writerow(result)
    outfile.close()
    
if __name__ == '__main__':
#     with open('PosDirection_Projection_Top10.pk') as f:
#         Pos = pickle.load(f)
#     for k in Pos.keys():
#         print k, '=== ',
#         for i in Pos[k].keys():
#             print i, ': ', Pos[k][i]
            
    print "WMD calculation initializing..."
    [vec_size, model] = load_vector_file('word2vec_new_word.model')
#     '''</start>修改此部分, 必要的输入为2个list: word2vec向量X和权重向量Weight_X, 职位名列表Pos可选 '''
#     with open('wmdVectors.pk') as f:
    with open('Pos_Direction_Vectors.pk') as f:
        [Pos, X, Weight_X] = pickle.load(f)
#     pos_Direction_Projection() 
#     most_Similar_Member()
    while True:
        query = raw_input('job title: ')
        query2 = raw_input('job title: ')
        print WMD_bt_2texts(query, query2)
#         print WMD_bt_queryAndLib(query, Pos, X, Weight_X)      # calculate and return the list of WMD between query and each job title in Library  
#     '''</end>'''
#     WMD_bt_EachOther_inLib(Pos, X, Weight_X)            
    print "WMD calculation complete..."


    