# -*- coding: utf-8 -*-
#!/usr/bin/python
'''Edited and Annotated by Haoming@iPIN on Sept, 2015'''

import sys, pickle, os
from tgrocery import Grocery
sys.path.append('new_word')
from word_cut import jieba
# import jieba
reload(sys)
sys.setdefaultencoding('utf-8')


symbol = ['（', '）', '(',')','[',']','{','}','，',',', '、', '。','～',':','：', ';','?','/','^','`','@','＠','《', '》', '—', '；','!','！','"','“','”',"-", ',','\\','&','＆','－','|','\\\'','／','【','】',"",
                 '•','*','-','~','<','>','…','·','=',"或","和","以及","及","等","技术要求","任职要求","职位需求","工作内容","岗位职责","工作职责","职位描述", '任职资格',
                 "本人","主要","负责","根据","通过","参与","解决","相关","进行","利用", "工作目标", "职责任务", "岗位要求"
                 "Job Purpose", "Job Objectives","Responsibilities","and","Main Tasks",'\t',' '
                 ]

initial = ["1","2","3","4","5","6","7","8","9", "一","二","三","四","五","六","七","八","九","十"]

'''清洗文本，去掉相关的标点符号和停用词'''
def clean(text):
    text = text.decode('utf-8').upper()
    newText = ''
    for i in symbol :
        text = text.replace(i, '')
    if '兼' in text and '兼职' not in text:
        text = text.replace('兼', '')
    if '+' in text and 'C++' not in text:
        text = text.replace('+', '')
    if '＋' in text and 'C＋＋' not in text:
        text = text.replace('＋', '')
    if '#' in text and 'C#' not in text:
        text = text.replace('#', '')
    if '＃' in text and 'C＃' not in text:
        text = text.replace('＃', '')
    if '.' in text and '.NET' not in text:
        text = text.replace('.', '')
    if ' ' in text and not text.replace(' ', '').isalnum():
        text = text.replace(' ', '')
    for wd in text:
        if wd == '\n':
            continue
        else:
            newText += wd
    for i in initial:
        if i in newText:       
            newText = newText.replace(i, '')
            break
    return newText

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

''' 读取四级职业方向树 '''
def read_hierPos():
    infile = open('jds_to_pan/out_list.txt')
    data = open('hierPos_Dict.pk', 'w')            # store the pickle of a dictionary of hierarchical position trees
    dict = {}
    for line in infile.readlines():
        index, hier = line.strip().split(':')
        full = hier.strip()         # full hierarchical structure of a position direction
        if '/' in full:
            full = full.replace('/', '_')
        if not dict.has_key(index):
            dict[index] = full
    pickle.dump(dict, data)

''' 从多个职位方向index为名的文件夹中, 读取相关样本, 打上index label并分词 '''
def read_Samples():
    path = 'jds_samples'
    dirList = os.listdir(path)
    train = open('prepData_raw', 'w')
    test = open('testSet_raw', 'w')
    FS = open('sample2Dict.pk', 'w')       # pickle file to save the pre-processed data
    TS = open('test2List.pk', 'w')
    Dict = {}	                  # store the sample texts for feature selection(labeled by class index)
    List = []                       # store the test texts for prediction
    benchmark = []          # store the benchmark labels for accuracy check
    trainText = []      
    testText = []       
    for Dir in dirList:
        if 'txt' in Dir:
            continue
        else:
            dirName = os.path.join(path, Dir)
            print '**** %s ****' % dirName
            fileList = os.listdir(dirName)
            Dict[Dir] = []      # store the sample texts for feature selection(each sample text is an element in the list)
            count = 0
            for file in fileList:
                fileName = os.path.join(dirName, file)
                infile = open(fileName, 'r')
                sample = Dir + '/x01'
                print '-%s' % fileName
                engCount = 0        # percentage of english content
                lineCount = 0           # number of lines 
                for line in infile.readlines():
                    lineCount += 1
                    line = line.strip()
#                     line = clean(line)
                    if not line == '':
#                         lineCount += 1
#                         sample += segmentation(line)
                        sample += line.encode('utf8')
#                     if clean(line)
                sample += '\n'
                count += 1
                if count > 20:		        # left 20 samples to be used for testing the classifiers
                    train.write(sample)
                    index, content = sample.split('/x01')
                    trainText.append((Dir, content.strip()))
                    Dict[Dir].append(text2word(sample.strip()))
                else:
                    index, content = sample.split('/x01')
                    testText.append((Dir, content.strip()))
                    List.append(text2word(sample.strip()))
                    benchmark.append(index)
                    test.write(sample)
    pickle.dump([trainText, testText], open('SampleSeg.pk', 'w'))                
    pickle.dump(Dict, FS)   
    pickle.dump((benchmark, List), TS)

''' 将一段已经分词后的文本储存为以词为单位元素的list中 '''
def text2word(text):
    List = []
    label, jd = text.split('/x01')
    seg = jieba.cut(jd)
    for wd in seg:
        if wd not in symbol and wd != ' ':
            List.append(wd.encode('utf8'))
    return List

'''用TextGrocery训练分类器并检查预测的准确率'''
def tGrocery():
    outFile = open('testResult.tmp', 'w')
    [trainingSet, benchmark] = pickle.load(open('SampleSeg.pk'))
    testingSet = []
    correctLabel = []
    for i in xrange(len(benchmark)):
        print '%d out of %d' % (i, len(benchmark))
        testingSet.append(benchmark[i][1])
        correctLabel.append(benchmark[i][0]) 
    grocery = Grocery('test')
    grocery.train(trainingSet)
    grocery.save()
    # load
    new_grocery = Grocery('test')
    new_grocery.load()
    Prediction = []
    for i in xrange(len(testingSet)):
        print '%d out of %d' % (i, len(testingSet))
        prediction = new_grocery.predict(testingSet[i])
        Prediction.append(prediction)
        temp = correctLabel[i] + '<-->' + prediction + '  /x01' + testingSet[i] + '\n'
        outFile.write(temp)
    correct = 0
    for i in xrange(len(Prediction)):
        print Prediction[i], correctLabel[i],
        if Prediction[i] == correctLabel[i]:
            correct += 1
            print 'Correct'
        else:
            print 'False'
    print 'Correct Count:', correct
    print 'Accuracy: %f' % (1.0 * correct / len(Prediction))
     
# read_Samples()
# tGrocery()
# read_hierPos()

if __name__ == '__main__':
#     while True:
#         input1 = raw_input("--")
#         c = clean(input1)
#         print c
#         print c.isalnum()
#         print segmentation(input1)

