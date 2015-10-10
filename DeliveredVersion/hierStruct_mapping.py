# -*- coding: utf-8 -*-
#!/usr/bin/python
'''Edited and Annotated by Haoming@iPIN on August, 2015'''

import sys, pickle
import get_wmdDist
reload(sys)
sys.setdefaultencoding('utf-8')

# model = gensim.models.word2vec.Word2Vec.load('word2vec_new_word.model') # load word2vec model
IDF = 'IDF.pk'      # absolute file path of IDF stored offline

'''load the hierarchical structure of the position tree extracted from Lagou'''
''' top 2 bottom structure (used for mapping when starting from top layer)'''
def top2bot_hier_struct():
    infile = open('../src/lagou.csv', 'r')
    topLayer = {}                                   # the top layer of the position tree
    for item in infile.readlines():
        top, mid, bot = item.strip().split(',', 2)
        if not topLayer.has_key(top):
            topLayer[top] = {}                      # the middle layer of the position tree
        if not topLayer[top].has_key(mid):
            topLayer[top][mid] = []               # the bottom layer of the position tree
        topLayer[top][mid].append(bot)
    for t in topLayer.keys():
        print '--------【%s】--------' % t
        for m in topLayer[t].keys():
            print '{%s}:' % m,
            for b in topLayer[t][m]:
                print '%s,' % b,
            print 
        print 

'''load the hierarchical structure of the position tree extracted from Lagou'''
''' bottom 2 layer structure (used for mapping when starting from bottom layer)'''    
def bot2top_hier_struct(Dict):
    infile = open('../src/lagou.csv', 'r')
    outfile = open('lagou.lib', 'w')
    for item in infile.readlines():
        top, mid, bot = item.lower().strip().split(',', 2)
        if not Dict.has_key(bot):
            Dict[bot] = [mid]
            Dict[bot].append(top)
        else:
            print bot
            Dict[bot].append(mid)
            Dict[bot].append(top)
            
    for job in Dict.keys():
#         print '%s -- %s -- %s ' % (job, Dict[job][0], Dict[job][1])
#         if len(Dict[job]) > 2:
#             print '%s -- %s -- %s ' % (len(job) * ' ', Dict[job][2], Dict[job][3])
        outfile.write('%s\n' % job)
#     return Dict

def testSet():
    with open('testingSet') as f:
        for query in f.readlines():
            query = query.strip()
            printer(query)

def printer(query):
    match = get_wmdDist.WMD_bt_queryAndLib(query, Pos, X, Weight_X)
    print 'Input: %s' % query
    print '%s <--- [%s] <---【%s】' % (match, Dict[match][0], Dict[match][1])
    if len(Dict[match]) > 2:
        print '%s <--- [%s] <---【%s】' % (len(match) * ' ', Dict[match][2], Dict[match][3])
#             print 
    
if __name__ == '__main__':
    with open('lagouVectors.pk') as f:
        [Pos, X, Weight_X] = pickle.load(f)
    Dict = {}                               # a dictionary storing the positions and their upper categories
    bot2top_hier_struct(Dict)
    testSet()
    while True:
        query = raw_input('job title: ')
        printer(query)
        print 
