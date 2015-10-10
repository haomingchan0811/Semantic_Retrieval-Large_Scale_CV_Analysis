# -*- coding: utf-8 -*-

import fileinput
import os
import random
from sklearn import svm
import datetime
import numpy as np
import imp

fp5, pn5, desc5 = imp.find_module('bns', ['../demo', ])
bns = imp.load_module('bns', fp5, pn5, desc5)

path = "/home/xuelong/ipin/company_industry/"

feature_dic = {}
feature_size = 0

indu_id_mapping = {}
id_indu_mapping = {}
indu_size = 0
bns_dic = {}

def load_feature():
    global feature_size
    global indu_size
    feature_path = path + "word_fs/chi4/"
    i = -1
    c = -1
    for filename in os.listdir(feature_path):
        if "~" in filename:
            continue
        i = i + 1
        indu_id_mapping[filename] = i
        id_indu_mapping[i] = filename
        for fi in fileinput.input([feature_path + filename]):
            f = fi.split('\t') 
            if f[0] not in feature_dic:
                c += 1
                feature_dic[f[0]] = c
        fileinput.close()
    feature_size = len(feature_dic)
    indu_size = len(indu_id_mapping)
    print "------ industry id ------"
    for k, v in indu_id_mapping.items():
        print k, v
    print "feature size", feature_size

def get_feature(word_list):
    vec = []
    for word in word_list:
        if word in feature_dic:
            vec.append(word)
    return vec

def get_comp(comp_f):
    return comp_f[0]
def get_indus(comp_f):
    return comp_f[1]
def get_comp_pos(comp_f):
    return comp_f[2]
def get_comp_desc(comp_f):
    return comp_f[3:]


def pro_indus(indus):
    z = []
    for indu in indus.split(','):
        if indu in indu_id_mapping:
            z.append(indu_id_mapping[indu])
    return z

def c_indu(z):
    z = sorted(z)
    for i in z:
        r = str(i) + ','
    return r[0:len(r) - 1]
    
def ltos(l):
    z = ""
    for v in l:
        z += str(v) + ','
    return z[0:len(z) - 1]
    
x_data = []
y_data = []


def get_bns_vec():
    print "get_bns_vec..."
    word_dic = {}
    global bns_dic
    for i in xrange(len(x_data)):
        vec = x_data[i]
        ys = ltos(y_data[i][1])
        if ys not in word_dic:
            word_dic[ys] = []
        word_dic[ys].append(vec)
    bns_dic = bns.get_bns(word_dic)
    

def load_data():
    data_path = path + "comp_desc_cut2"
    t = 0
    c = 0
    global doc_total
    for comp_raw in fileinput.input([data_path]):
        c += 1
        comp_raw = comp_raw.replace('\n', '')
        comp_f = comp_raw.split()
        # comp = get_comp(comp_f)
        indus = get_indus(comp_f)
        induids = pro_indus(indus)
        comp_desc = get_comp_desc(comp_f)
        if len(induids) == 0 or len(comp_desc) == 0:
            continue
        vec = get_feature(comp_desc)
        if len(vec) >= 2:
            if t % 5000 == 0:
                print "load data size : ", t
            t = t + 1
            x_data.append(vec)
            y_data.append([c, induids])
    doc_total = t
    print "load total data size : ", t

x_train = []
y_train = []
x_test = []
y_test = []

def pretreat():
    print "pretreat..."
    dsize = len(x_data)
    train_rag = range(dsize)
    train_samp = random.sample(train_rag, 30000)
    for i in train_rag:
        data = x_data[i]
        ys = y_data[i]
        if i in train_samp:
            x_train.append(data)
            y_train.append(ys[1])
        else:
            x_test.append(data)
            y_test.append(ys)

clf_dic = {}

def toBns():
    print "toBns..."
    for induid in id_indu_mapping.keys():
        print "------------", induid
        Y = []
        X = []
        for i in xrange(len(y_train)):
            induids = y_train[i]
            ws = x_train[i]
            y = 1 if induid in induids else 0
            Y.append(y)
            vec = [0.0] * feature_size
            ll = float(len(ws))
            for w in ws:
                vec[feature_dic[w]] += bns_dic[w][str(induid)] / ll
                # print w, feature_dic[w], bns_dic[w][str(induid)]
            X.append(vec)
        clf = svm.LinearSVC(C=5, penalty='l2', dual=True)
        clf.fit(X, Y)
        clf_dic[induid] = clf

def predict():
    print "predict..."
    yd_dic = {}
    for induid, clf in clf_dic.items():
        X = []
        for i in xrange(len(x_test)):
            ws = x_test[i]
            vec = [0.0] * feature_size
            ll = float(len(ws))
            for w in ws:
                vec[feature_dic[w]] += bns_dic[w][str(induid)] / ll
            X.append(vec)
        y_ds = clf.decision_function(X)
        yd_dic[induid] = y_ds
        
    outfile = file(path + "pro/svm/bns_", 'w')
    th = -1
    for yrs in y_test:
        th += 1
        zz = str(yrs[0])
        for i in xrange(indu_size):
            zz += "," + str(yd_dic[i][th])
        for yr in yrs[1]:
            zz += "," + str(yr) 
        outfile.write(zz + "\n")
    outfile.close()

def bz(l1, l2):
    for l in l1:
        if l in l2:
            return True
    return False

def pro_pre(yd, yr):
    max_idx = -1
    max_f = 0.0
    fir = True
    for i in xrange(indu_size):
        d = yd[i]
        if fir :
            max_f = d
            max_idx = i
            fir = False
        elif d > max_f:
            max_f = d
            max_idx = i
    sec_max_idx = -1
    fir = True
    for i in xrange(indu_size):
        d = yd[i]
        if fir:
            if max_idx != i:
                max_f = d
                sec_max_idx = i
                fir = False
        elif i == max_idx:
            pass
        elif d > max_f:
            max_f = d
            sec_max_idx = i
    return [max_idx, sec_max_idx]

def bg(zl):
    zz = ""
    for z in zl:
        zz += str(z) + '+'
    return zz

def test():
    global indu_size
    indu_size = 19
    y_ds = []
    y_test = []
    y_row = []
    y_indu = {}
    for mll in fileinput.input([path + "pro/svm/bns_"]):
        mls = mll.replace('\n', '').split(',')
        msize = len(mls)
        l1 = []
        l2 = []
        for i in xrange(msize):
            m = mls[i]
            if i == 0:
                y_row.append(int(m))
            elif i <= indu_size:
                l1.append(float(m))
            else:
                m = int(m)
                if m not in y_indu:
                    y_indu[m] = 1
                else:
                    y_indu[m] += 1
                l2.append(m)
        y_ds.append(l1)
        y_test.append(l2)
        
    w_dic = {}
    for i in xrange(indu_size):
        w_dic[i] = 0   
    
    r = 0
    w = 0
    ii = -1
    for yd in y_ds:
        ii += 1
        yr = y_test[ii]
        yrowid = y_row[ii]
        z = pro_pre(yd, yr)
        if bz(z, yr):
            r += 1
            # print z, bg(yr), yrowid, yd
        else:
            for g in yr:
                w_dic[g] += 1
            w += 1
            print z, bg(yr), yrowid, yd
    print  r, w, float(r) / (r + w)
    for g, c in w_dic.items():
        print g, c, y_indu[g], float(y_indu[g] - c) / y_indu[g]
    
    

def main():
    load_feature()
    load_data()
    get_bns_vec()
    pretreat()
    toBns()
    predict()
    
test()
