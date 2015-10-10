# -*- coding: utf-8 -*-
#!/usr/bin/python
'''Edited and Annotated by Haoming@iPIN on August, 2015'''

import os, sys, pickle, string
# import gensim
import numpy as np
sys.path.append('WMD_code/python-emd-master')
from emd import emd
sys.path.append('new_word')
from word_cut import jieba
# import jieba
reload(sys)
sys.setdefaultencoding('utf-8')

# model = gensim.models.word2vec.Word2Vec.lo('word2vec_new_word.model') # load word2vec model
# model = gensim.models.word2vec.Word2Vec.load_word2vec_format('word2vec_new_word.model', binary = False) # load word2vec model(c format)
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

''' read data set line by line and fetch the word vectors '''
def read_posDict(dataset):
    f = open(dataset)
    # initialize matrixes and relevant variables
    num_lines = sum(1 for line in open(dataset))               # number of documents                                   
    X = np.zeros((num_lines,), dtype=np.object)                # w2v vectors matrix, iTH column is the iTH document's w2v matrix
    Weight_X = np.zeros((num_lines,), dtype=np.object)   # Weight vectors matrix, iTH column is the iTH document's Weight matrix
    count = 0                                                                       # current iterated document
    Pos = []                                                                          # store the job title in original order
    
    for line in f:
        Pos.append(line.strip())
        line = clean(line)
        line = segmentation(line.lower())
        W = line.split()                                                     # split the words apart
        (Fs, weight) = generateVec(W)
        X[count] = Fs.T                                                    # store the w2v vectors matrix of the countTH document, each row is a w2v word vector
        Weight_X[count] = weight                                   # store the Weight vectors of the countTH document
        count = count + 1
        if count % 100 == 0:
            print '%d out of %d complete...' % (count, num_lines)
    return (Pos, X, Weight_X)

''' calculate the vectors of words (including the w2v vectors as well as the weight vectors) '''
def generateVec(W):
    # store each word's vector in a column
    F = np.zeros((vec_size,len(W)))
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

''' overall function to transform a position(job title) into vectors'''
def pos2vec():
    print "Vectors generation initializing..."
    # 1. specify train/test data sets
    '''修改此部分, 输入为去重后的职位名文本文件,每个职位名占一行'''
#     train_dataset = 'lagou.lib'                  # absolute file path of the training data set
#     save_file = 'lagouVectors.pk'   # absolute file path of the saved vectors of training set
    train_dataset = '../src/Pos_direction'                  # absolute file path of the training data set
    save_file = 'Pos_Direction_Vectors.pk'   # absolute file path of the saved vectors of training set
    # 2. read document data
    (Pos, X, Weight_X)  = read_posDict(train_dataset)
    # 3. save pickle of extracted variables
    with open(save_file, 'w') as f:
#         pickle.dump([Pos, X.tolist(), Weight_X.tolist()], f)
        pickle.dump([Pos, X, Weight_X], f)
        f.close()

if __name__ == '__main__':
    [vec_size, model] = load_vector_file('word2vec_new_word.model')
    pos2vec()   
    print "Vectors generation complete..."
    