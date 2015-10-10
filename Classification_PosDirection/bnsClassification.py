# -*- coding: utf-8 -*-
import math, pickle, csv
import numpy as np
from numpy import vstack
from sklearn import svm

def dedup(items):
    temp_dic = {}
    for item in items:
        if item not in temp_dic:
            temp_dic[item] = 1
    return temp_dic.keys()

'''
txt_dic  key - 文档类型
value - 该文档类型下所以文档的集合
'''

def get_in_range(r):
    if r < 0.0005:
        return 0.0005
    elif r > (1 - 0.0005):
        return (1 - 0.0005)
    else:
        return r
    
    
def get_chi(txt_dic):
    class_dic = {}
    # classes = len(txt_dic)
    # key - word  value - 所有类下word出现的文档数
    word_dic = {}
    class_type_list = txt_dic.keys()
    n = 0
    for class_type, txt_list in  txt_dic.items():
        txt_count = len(txt_list)
        n += txt_count
        tw_dic = {}  # key - word  value - class_type类下word出现的文档数
        for txt in txt_list:
            words = dedup(txt)
            for w in words:
                if w not in tw_dic:
                    tw_dic[w] = 1
                else:
                    tw_dic[w] += 1
                if w not in word_dic:
                    word_dic[w] = 1
                else:
                    word_dic[w] += 1
        class_dic[class_type] = [txt_count, tw_dic]
        
    # word_count = float(len(word_dic))
    count = 1
    wd = len(word_dic)
    for w, wc in word_dic.items():
        print '%d out of %d features...' % (count, wd)
        count += 1
        # wc表示出现w的文档数
        bns_dic = {}
        for class_type in class_type_list:
            txt_count = float(class_dic[class_type][0])
            # 每个词在class_type类出现的文档数
            tw_dic = class_dic[class_type][1]
            a = 0.0 if w not in tw_dic else float(tw_dic[w])
            c = txt_count - a
            b = wc - a
            d = (n - txt_count) - b
            tpr = get_in_range(a / float(a + c))
            fpr = get_in_range(b / float(b + d))
            bns_dic[class_type] = abs(ltqnorm(tpr) - ltqnorm(fpr))
            print w,class_type, bns_dic[class_type]
        # print w,mi_max,ct
        word_dic[w] = bns_dic
    print 
    f = open('BNS.pk', 'w')       # pickle file to save the pre-processed data
    pickle.dump(word_dic, f)
    return word_dic

''' Inverse standard normal cumulative distribution function'''
def ltqnorm(p):
    """
    Modified from the author's original perl code (original comments follow below)
    by dfield@yahoo-inc.com.  May 3, 2004.

    Lower tail quantile for standard normal distribution function.

    This function returns an approximation of the inverse cumulative
    standard normal distribution function.  I.e., given P, it returns
    an approximation to the X satisfying P = Pr{Z <= X} where Z is a
    random variable from the standard normal distribution.

    The algorithm uses a minimax approximation by rational functions
    and the result has a relative error whose absolute value is less
    than 1.15e-9.

    Author:      Peter John Acklam
    Time-stamp:  2000-07-19 18:26:14
    E-mail:      pjacklam@online.no
    WWW URL:     http://home.online.no/~pjacklam
    """

    if p <= 0 or p >= 1:
        # The original perl code exits here, we'll throw an exception instead
        raise ValueError("Argument to ltqnorm %f must be in open interval (0,1)" % p)

    # Coefficients in rational approximations.
    a = (-3.969683028665376e+01, 2.209460984245205e+02, \
         - 2.759285104469687e+02, 1.383577518672690e+02, \
         - 3.066479806614716e+01, 2.506628277459239e+00)
    b = (-5.447609879822406e+01, 1.615858368580409e+02, \
         - 1.556989798598866e+02, 6.680131188771972e+01, \
         - 1.328068155288572e+01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01, \
         - 2.400758277161838e+00, -2.549732539343734e+00, \
          4.374664141464968e+00, 2.938163982698783e+00)
    d = (7.784695709041462e-03, 3.224671290700398e-01, \
          2.445134137142996e+00, 3.754408661907416e+00)

    # Define break-points.
    plow = 0.02425
    phigh = 1 - plow

    # Rational approximation for lower region:
    if p < plow:
        q = math.sqrt(-2 * math.log(p)) 
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)

    # Rational approximation for upper region:
    if phigh < p:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
                ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)

    # Rational approximation for central region:
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    
def getBNS(All, bns):
    f = open('selected_Feature.pk', 'r')
    selected = pickle.load(f)   # selected features
    name = []
    for  i in xrange(len(selected)):
        name.append(selected[i][0])
    selected = set(name)
    features = []                     # store the features in order as the column of the matrix
    count = 0
    lookUpFeature = {}      # a dictionary to store the index of each feature in the matrix
    for i in bns.keys():
        if i in selected:
            features.append(i)
            lookUpFeature[i] = count 
            count += 1
    print 'bns preparation complete...'
#     print features, lookUpFeature
    return features, lookUpFeature

'''remain the selected label and let others be 0'''
def binarize(cur, label):
    if cur == label:
        return label
    else:
        return 0

def save_Result(prediction):
    print 'saving Prediction result...'                         
    infile = open('bns_Prediction.csv', 'w')
    lines = csv.writer(infile)
    lines.writerow(['testId', 'Label'])
    index = 1
    for item in prediction:
        tmp = [index, item]
        lines.writerow(tmp)
        index += 1
        
''' generate a BNS matrix for the label L and non-L of the training set'''
def generate_trainMatrix(All, features, lookUpFeature, bns, L):
    print 'generating training matrix for label %s...' % L
    n_features = len(features)
#     Matrix = np.zeros((n_features))     # a sparse matrix for training
#     Labels = np.zeros((1))          # a matrix to store the labels in order
    Matrix = []
    Labels = []         # numpy is god damn slow!!!! replaced with List type
    n_samples = 0
#     count = 0
    n = 0
    for k in All.keys():
        print 'label %d' % n
        n += 1
        samples = All[k]
        n_samples += len(samples)
        c = 0
        for text in samples:
#             vector = np.zeros((n_features))
#             print '--test in samples %d ' % c
            c += 1
            count = 0
            vector = [0.0] * n_features
            for wd in text:
#                 print '== wd in text %d' % count
                count += 1
                try:
                    index = lookUpFeature[wd]           # the index of the word in the feature order
                    vector[index] = bns[wd][L]
                except KeyError:
#                     print "KeyError"
                    continue
#             if count == 0:
#                 Matrix = vector
#                 Labels = binarize(k, L)
#                 count += 1
#             else:
#                 Matrix = vstack((Matrix, vector)) 
#                 Labels = vstack((Labels, binarize(k, L)))
            Matrix.append(vector)
            Labels.append(binarize(k, L))

    return Matrix, Labels

def trainClassifier(trainMatrix, trainLabel, label):
    print 'Training SVM Classifier for label %s...' % label
    classifier =  svm.LinearSVC(C = 5.0)               
    classifier.fit(trainMatrix, np.ravel(trainLabel))
#     print classifier
    return classifier

def saveClassifier(All, bns, features, lookUpFeature):
    CLF = {}                            # store the classifiers for future classification
    count = 1
    num = len(All)
    for label in All.keys():
        Matrix, Labels = generate_trainMatrix(All, features, lookUpFeature, bns, label)
        print '%d out of %d: ' % (count, num),
        count += 1
        clf = trainClassifier(Matrix, Labels, label)
        CLF[label] = clf
    print 'saving all %d SVM Classifiers...' % len(CLF) 
    return CLF
        
''' generate a BNS vector for the label L of the data which is to be predicted'''
def generate_testVector(text, features, lookUpFeature, bns, L):
    vector = np.zeros((len(features)))
    for wd in text:
        if wd in lookUpFeature.keys():          # the word is a feature
            index = lookUpFeature[wd]           # the index of the word in the feature order
            vector[index] = bns[features[index]][L]
    return vector

'''for each test data in the testSet, plunge it into all classifiers and predict the most possible label'''
def predict(All, testSet, CLF, features, lookUpFeature, bns):  
    print 'prediction initializing...'
    prediction = []
    for i in xrange(len(testSet)):
        text = testSet[i]
#         print text
        possibility = []    # the distance between the testVec and the decision boundry
        for label in All.keys():
            testVec = generate_testVector(text, features, lookUpFeature, bns, label)
            clf = CLF[label]
#             testLabel = int(clf.predict(testVec))
            dist = float(clf.decision_function(testVec))
            possibility.append((label, dist)) 
        predict_Label = selectBest(possibility)
        print '%d case: %d' % (i, predict_Label)
        prediction.append(predict_Label)
    print 'prediction complete...'
    return prediction
        
'''select the most possible label among all classifiers'''        
def selectBest(possibility):
#     print possibility
    sort_Dist = sorted(possibility, key = lambda d: d[1], reverse = True)
    return sort_Dist[0][0]
        
'''check the accuracy of the prediction'''
def accuracy(prediction, benchmark):
    count = 0
    n = len(prediction)
    for i in xrange(n):
        if prediction[i] == benchmark[i]:
            count += 1
    percentage = count * 1.0 / n
    print 'prediction accuracy: %f' % percentage

'''overall function to determine which class the data should be categorized into'''
def pos_classification():
    print 'initializing data files...'
    f = open('sample2Dict.pk', 'r')
    fs = open('test2List.pk', 'r')
    bs = open('BNS.pk', 'r')
    benchmark, testSet = pickle.load(fs)
    All = pickle.load(f)
    bns = pickle.load(bs)
    print 'data files load complete...'

#     All = {'1':[['book', 'good', 'girl']], '3':[['study', 'job','haoming'], ['study', 'book', 'good'], ['book', 'study']],'2':[['girl','xuelong']]}
#     testSet = [['book', 'good', 'girl'], ['study', 'job','haoming'], ['xuelong','book']]
#     benchmark = ['1','3','2']
#     bns = get_chi(All)
    
    features, lookUpFeature = getBNS(All, bns)
    CLF = saveClassifier(All, bns, features, lookUpFeature)
    result = predict(All, testSet, CLF, features, lookUpFeature, bns)
    accuracy(result, benchmark)

if __name__ == '__main__':
#     f = open('sample2Dict.pk', 'r')
#     All = pickle.load(f)
#     bns = get_chi(All)
    pos_classification()
    
    
    