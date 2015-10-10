# -*- coding: utf-8 -*-
#!/usr/bin/python
'''Edited and Annotated by Haoming@iPIN on August, 2015'''

import os, sys, pickle, math
sys.path.append('new_word')
from word_cut import jieba
# import jieba
reload(sys)
sys.setdefaultencoding('utf-8')

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

'''Inverse Document Frequency'''
def IDF(inputFile = '../src/Pos_frequency'):
    IDFdict = {}        # record the IDF of every word
    infile = open(inputFile, 'r')
    outfile = open('IDF.out', 'w')
    end = 0
    while not end:
        line = infile.readline().strip().encode('utf-8')
        if line != '':
            print line
            line = clean(line)
            print line
            seg = jieba.cut(line)
            W = ''
            for i in seg:
                W += i + ' '
                if i not in IDFdict.keys():
                    IDFdict[i] = 1
                else:
                    IDFdict[i] += 1
            print W
        else:
            end = 1
    
    Len = len(IDFdict)                                                  #Total number of words
    for i in IDFdict.keys():
        IDFdict[i] = math.log(Len / IDFdict[i])                 # IDF of each word
        outfile.write('%s %s\n' % (i, IDFdict[i]))

    data = open('IDF.pk', 'w')            #serialize the IDF dictionary into pickle file
    pickle.dump(IDFdict, data)
    data.close()
    
if __name__ == '__main__':
    inputFile = '../src/rawPos'
    IDF(inputFile)
#     IDF()
    