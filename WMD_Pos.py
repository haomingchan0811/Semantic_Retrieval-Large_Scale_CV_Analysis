# -*- coding: utf-8 -*-
#!/usr/bin/python

'''Edited and Annotated by Haoming Chen@iPIN on August, 2015'''

import os, gensim, pdb, sys, pickle, string, jieba
import scipy.io as io
import numpy as np
import multiprocessing as mp
sys.path.append('WMD_code/python-emd-master')
# from emdTEST import emd
# import emdTEST
from emd import emd
reload(sys)
sys.setdefaultencoding('utf-8')

# load word2vec model
model = gensim.models.word2vec.Word2Vec.load('word2vec_model/word2vec.model')
vec_size = 50

''' given a text, return its segmentation with blank space in-between '''
def segmentation(text):
    newText = ''
    text = text.strip()
    text = text.translate(string.maketrans("",""), string.punctuation)  # remove the punctuation
    seg = jieba.cut(text)
    for wd in seg:
        newText += wd
        newText += ' '
    return newText.strip()


''' read dataset line by line and fetch the word vectors '''
def read_stdDict(dataset):
    # get stop words (deleted on Aug. 12th, 2015)
    f = open(dataset)
    # initialize matrixes and relevant variables
    num_lines = sum(1 for line in open(dataset))               # number of documents                                   
    X = np.zeros((num_lines,), dtype=np.object)                # w2v vectors matrix, iTH column is the iTH document's w2v matrix
    Weight_X = np.zeros((num_lines,), dtype=np.object)   # Weight vectors matrix, iTH column is the iTH document's Weight matrix
    count = 0                                                                       # current iterated document
    the_words = np.zeros((num_lines,), dtype=np.object)  # store the documents without repeating words
    Pos = {}                                                                         # store the job title in original order
    
    for line in f:
#         print '%d out of %d' % (count+1, num_lines)
        Pos[count] = line.strip()
        line = segmentation(line.lower())
        W = line.split()                                 # split the words apart
        print '---------------------------------------------'
        print line
        (Fs, word_orders, weight) = Weight(W)
        # eliminate the 0 columns and transpose, now each row is a w2v word vector
        X[count] = Fs.T                                                    # store the w2v vectors matrix of the countTH document
        the_words[count] = word_orders                        # store the non-repeating words in order of the countTH document
        Weight_X[count] = weight                                     # store the BOW vectors of the countTH document
        count = count + 1
        
#     n = np.shape(X)
#     n = n[0]                                                # number of documents 
#     for i in xrange(n):
#         bow_i = BOW_X[i]                            # the BOW vector matrix of the iTH document
#         bow_i = bow_i / np.sum(bow_i)        # calculate the word frequency of each word in the document
# #         bow_i = bow_i.tolist()                       # transform into List type
#         BOW_X[i] = bow_i                            
# #         X_i = X[i].T                                       # the transpose of the iTH document's w2v vectors matrix, now each row represents a word's w2v vector 
#         X_i = X_i.tolist()                                # transform into List type
#         X[i] = X_i
    return (Pos, X, Weight_X, the_words)

''' calculate the weight vectors of words'''
def Weight(W):
    # store each word's vector in a column
    F = np.zeros((vec_size,len(W)))
    # store the split words in order: repeated word will be stored in its first occurrence and then stored as '' afterwards
    word_order = np.zeros((len(W)), dtype=np.object)  
    inner = 0                                         # iterator for the split words
#     idf_set = pickle.load(open('src/IDF.pk'))
    idf_set = pickle.load(open('DeliveredVersion/IDF.pk'))
    # BOW vector: number of occurrence of each word in the word_order matrix
    bow_x = np.zeros((len(W),))
    idf_x = np.zeros((len(W),))               # IDF of each non-repeat words 
    weight = np.zeros((len(W),))            # Final Weight of each non-repeat words
    for word in W[0 : len(W)]:                   
        word = word.decode('utf-8')
        try:
            test = model[word]                  # w2v embedding word vector
            if word in word_order:
                IXW = np.where(word_order==word)
                bow_x[IXW] += 1                 # number of occurrence of the repeated word recorded at its first occurrence position
                word_order[inner] = ''          # repeated word will be stored as '' for the 2nd or later occurrence 
            else:
                word_order[inner] = word    # store the word at its first occurrence
                bow_x[inner] += 1                # number of occurrence of the word 
                if idf_set.has_key(word):       # IDF of the word
                    idf_x[inner] = idf_set[word]    
                else:
                    idf_x[inner] = 1.38            # if IDF does not exist, the word will be given a rather small weight (Reference: IDF(经理) = 1.38629436112)                  
                F[:,inner] = model[word]      # load the corresponding w2v word vector into the corresponding column 
        except KeyError, e:
            word_order[inner] = ''
        inner = inner + 1
    word_orders = word_order[word_order != '']     # remove the ''s(representing repeated words)
    bow_xs = bow_x[bow_x != 0]                              # remove the 0s(representing repeated words)
    idf_xs =  idf_x[idf_x != 0]                                     # remove the 0s(representing repeated words)
    Fs = F.T[~np.all(F.T == 0, axis=1)]                      # F.T: transpose of the F matrix; '~': converse position logical(按位取反);
    bow_i = bow_xs                                                   # the BOW vector matrix of the document
    bow_i = bow_i / np.sum(bow_i)                            # calculate the word frequency of each word in the document
    bow_xs = bow_i                            
    
    idf_xs = idf_xs / np.sum(idf_xs)                             # normalize the IDF 
    weight = bow_xs + idf_xs                                     # Total weight combing the BOW weight and IDF
    return (Fs, word_orders, weight)

def std2vec():
    # 1. specify train/test datasets
    # Format: word1 word2 word3, punctuation and extra blank is allowed
#     train_dataset = 'src/STD.lib'             
#     save_file = 'src/STDvectors.pk'
    train_dataset = 'src/rawPos'             
    save_file = 'src/rawPos_vectors.pk'
    # 2. read document data
    (Pos, X, Weight_X, words)  = read_stdDict(train_dataset)
#     print Pos
#     print '---------------------'
#     print X 
#     print '---------------------'
#     print Weight_X
    
    # 3. save pickle of extracted variables
    with open(save_file, 'w') as f:
        pickle.dump([Pos, X, Weight_X, words], f)
        f.close()

# '''test section'''
#     train_dataset = 'test'             
#     (Pos, X, Weight_X, words)  = read_stdDict(train_dataset)
        
''' calculate the WMD distance between query text and each text in STD Library '''
def WMD_bt_queryAndLib(text, Pos, X, BOW_X):
# X:             w2v vectors matrix, iTH column is the iTH document's w2v vectors matrix
# BOW_X:   BOW(word frequency) vectors matrix, iTH column is the iTH document's BOW vectors matrix
# words:     store the documents without repeating words
#     with open('src/STDvectors.pk') as f:
#         [Pos, X, BOW_X, words] = pickle.load(f)
    n = np.shape(X)
    n = n[0]                                                # number of documents 
    Dist = []
    (Fs, wordOrders, weight) = Weight(segmentation(text.lower()).split())
#     print '-----------------W2V向量---------------'
#     print type(Fs)
#     print np.shape(Fs)
#     print Fs
#     print '---------------Weight向量----------------'
#     print type(weight)
#     print np.shape(weight)
#     print weight
#     print '---------------------------------------'
    text_BOWVec = weight.tolist()               # BOW word vector of text
    text_w2vVec = Fs.T.T.tolist()                   # w2v word vector of text
    for j in xrange(n):
        emdDist = emd((text_w2vVec, text_BOWVec), (X[j].T.tolist(), BOW_X[j].tolist()), distance)
        Dist.append((Pos[j], emdDist))     # calculate the EMD of two documents
        if emdDist == 0:                          # already find the same name in the standard library, jump out of the loop
            break
    sort_Dist = sorted(Dist, key = lambda d: d[1])
    print '-----------------------------------------------'
    if len(sort_Dist) >= 5:
        for i in range(5):
            print '%f    %s' % (sort_Dist[i][1], sort_Dist[i][0].encode('utf-8'))
    else:
        for i in range(len(sort_Dist)):
            print '%f    %s' % (sort_Dist[i][1], sort_Dist[i][0].encode('utf-8'))
    return sort_Dist[0][0]

''' Euclidian distance between two word vectors '''
def distance(x1,x2):                                
    return np.sqrt(np.sum((np.array(x1) - np.array(x2)) ** 2))

''' calculate the WMD distance between two texts '''
def WMD_bt_2texts(text1, text2):
    (Fs, wordOrders, weight) = Weight(segmentation(text1.lower()).split())
    text1_BOWVec = weight.tolist()               # BOW word vector of text
    text1_w2vVec = Fs.T.T.tolist()                   # w2v word vector of text
    (Fs, wordOrders, weight) = Weight(segmentation(text2.lower()).split())
    text2_BOWVec = weight.tolist()               # BOW word vector of text
    text2_w2vVec = Fs.T.T.tolist()                   # w2v word vector of text
    Dist = (emd((text1_w2vVec, text1_BOWVec), (text2_w2vVec, text2_BOWVec), distance))   # calculate the EMD of two documents
    return Dist

if __name__ == '__main__':
    std2vec()   # only have to run for the first time to save the pickle file
#     with open('src/STDvectors.pk') as f:
    with open('src/rawPos_vectors.pk') as f:
        [Pos, X, Weight_X, words] = pickle.load(f)
    while True:
        print 
        text1 = raw_input('job title: ')
#         text2 = raw_input('2nd job title: ')
#         print WMD_bt_2texts(text1, text2)
        print WMD_bt_queryAndLib(text1, Pos, X, Weight_X)



