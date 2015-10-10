#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, MiniBatchKMeans

import os
import string
reload(string)

stopwords = [u"-",u"、",u"，",u"(",u")",u"+",u"？",u"—",u"！",u"】",u"【",u"·",u" ",u",",u"（",u"）",u"~",u"!",u"．",u"<",u":",u".",u"\"",u"•",u">",u"《",u"》",u"/",u"//",u"。" ,"1","2","3","4","5","6","7","8","9","0", "10","11", 
                      u"负责",u"根据",u"通过",u"参与",u"解决",u"相关",u"进行",u"利用",u"能够",u"自己",u"跟",u"以及",u"和",u"工作",u"一个",u"主要",u"公司",u"一定",u"日常",u"其他",u"其它",u"兼职",u"实习",u"北京",u"集团",u"实习生",
                      u"应届",u"见习",u"临时",u"分公司",u"办事处",u"资深"]

o = open('pos_only_clu(k=f=3000)', 'w')

'''导入文本数据集'''
def loadDataset():
    f = open('src/Pos_frequency','r')
    dataset = []
    lastPage = ''
    for line in f.readlines():
        freq, name = line.split(' ')
        if freq >= 100:
            dataset.append(name)
    f.close()
    return dataset
   
def transform(dataset,n_features): ##1000
    vectorizer = TfidfVectorizer(stop_words=stopwords,max_df=0.5, max_features=n_features, min_df=2,use_idf=True)
    X = vectorizer.fit_transform(dataset)
    return X,vectorizer
 
def train(X,vectorizer,true_k,minibatch = False,showLable = False):
    #使用minibatch采样数据/所有原始数据训练k-means
    if minibatch:
        km = MiniBatchKMeans(n_clusters=true_k, init='k-means++', n_init=1,
                             init_size=1000, batch_size=1000, verbose=False)
    else:
        km = KMeans(n_clusters=true_k, init='k-means++', max_iter=300, n_init=2,n_jobs=-2,
                    verbose=False)
    km.fit(X)    
    if showLable:
        print("Top terms per cluster:")
        order_centroids = km.cluster_centers_.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names()
#         print (vectorizer.get_stop_words())
        for i in range(true_k):
            print("Cluster %d:" % i, end='')
            o.write("Cluster %d:" % i,)
            for ind in order_centroids[i, :3]:
                print(' %s' % terms[ind], end='')
                o.write(' %s' % terms[ind].encode('utf-8'))
            print()
            o.write('\n')
    result = list(km.predict(X))
#     print ('Cluster distribution:')
#     print (dict([(i, result.count(i)) for i in result]))
    return -km.score(X)
     
def test():
    '''测试选择最优参数'''
    dataset = loadDataset()    
    print("%d documents" % len(dataset))
    X,vectorizer = transform(dataset,n_features=500)
    true_ks = []
    scores = []
    for i in xrange(100,1000,100):        
        score = train(X,vectorizer,true_k=i)/len(dataset)
        print (i,score)
        true_ks.append(i)
        scores.append(score)
    plt.figure(figsize=(8,4))
    plt.plot(true_ks,scores,label="error",color="red",linewidth=1)
    plt.xlabel("n_features")
    plt.ylabel("error")
    plt.legend()
    plt.show()
    
def out(v,f):
    '''在最优参数下输出聚类结果'''
    dataset = loadDataschecet()
    X,vectorizer = transform(dataset,n_features=f)
    score = train(X,vectorizer,true_k=v,showLable=True)/len(dataset)
    print (score)
    
# test()
c = 100
f = 2000
while(c <= 500):
    while(f <= 5000):
        print('*****************************')
        print("Cluster: "+ "%d "%c + "  Feature: " + "%d"%f)
        out(c, f)
        f += 500
    c = c + 100
    f = 500
