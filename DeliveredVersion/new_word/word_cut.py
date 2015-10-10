#-*- coding:utf-8 -*-
import jieba
import os
with open(os.path.join(os.path.dirname(__file__),'new_word_v6.txt')) as f:
    for line in f:
        word,freq=line.split()
        jieba.add_word(word.lower().replace('/','_'),freq=freq)
cut_old=jieba.cut
def cut(sentence, cut_all=False, HMM=True):
    sentence=sentence.replace('/','_')
    return cut_old(sentence,cut_all,HMM)
jieba.cut=cut
