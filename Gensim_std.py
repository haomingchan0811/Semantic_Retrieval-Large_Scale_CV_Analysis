# -*- coding: utf-8 -*-
#!/usr/bin/python

import time
import os
import sys
import string
import jieba
import gensim, logging
logging.basicConfig(format = '%(asctime)s : %(levelname)s : %(message)s', level = logging.INFO)
reload(string)
reload(os)
reload(sys)
sys.setdefaultencoding('utf-8')

pos_std = {}

def Gensim(model, in_file):
    end = 0
    count = 1
    while not end:
        line = in_file.readline()
        if line != '': 
            start = time.clock()
            position, frequency = line.split(' ', 1)
            seg = jieba.cut(position)
            seg_line = ''
            for i in seg:
                seg_line += (i.encode('utf-8') + ' ')
            seg_line = seg_line.replace('\n', '')
            seg_line = seg_line[:-1]
            max_copy = 0
            print seg_line
            if count == 1:
                pos_std[seg_line] = []
            else:
                max = 0
                max_index = ''
                for key in pos_std.keys():
                    similarity = 0
                    compare = 0
                    for word1 in seg_line.split(' '):
                        for word2 in key.split(' '):
                            compare += 1
                            similarity += model.similarity(word1, word2)
                            print "'%s'-'%s'-'%f'" % (word1, word2, similarity)
                    ''' 两个职位的平均相似度 '''
                    similarity /= compare
    #                 print similarity
                    if max < similarity:
                        max = similarity
                        max_index = key
                ''' 超过阀值则归属到已有的职业类中'''
                if max > 0.5:    
                    pos_std[max_index].append(seg_line.replace(' ','').encode('utf8'))
                else:
                    pos_std[seg_line] = []
                max_copy = max
            stop = time.clock()
            print "Index: %d   Time: %f  Similarity: %f" % (count, stop - start, max_copy)
            count += 1
        else:
            end = 1
            
    i = 1
    sort_pos = sorted(pos_std.iteritems(), key = lambda d:len(d[1]), reverse = True)
    for key in pos_std.keys():
        pos = key.replace(' ','')
        print '%d %s:' % (i, pos),
        print ' '.join(pos_std[key])
        i += 1
    
def Format():
    input = open('src/Prep_pos_seg.out','r')
    sentences = []
    for line in input.readlines():
        if line != '':
            L = []
            for i in line.split(' '):
                L.append(i.encode('utf-8'))
            sentences.append(L)
    # min_count:丢弃少于该词频的单词　size:神经网络隐藏层的单元数
    model = gensim.models.Word2Vec(sentences, min_count = 5, size = 500, window= 5)
    model.save('src/pos_model')

def test():
    train = gensim.models.Word2Vec.load('src/pos_model')
    while True:
        pos1 = raw_input('1st position: ')
        pos2 = raw_input('2nd position: ')
        print train.similarity(pos1, pos2)
        
def main():
    train = gensim.models.Word2Vec.load('src/pos_model')
    input= open('src/Pos_2word_freq.direct','r')
    Gensim(train, input)
    
    