# -*- coding: utf-8 -*-
import pickle, math

''' function "dedup" and "get_chi" written by 薛隆 '''

def dedup(items):
    temp_dic = {}
    for item in items:
#         print item
        if item not in temp_dic:
            temp_dic[item] = 1
    return temp_dic.keys()

'''
txt_dic  key - 文档类型
value - 该文档类型下所以文档的集合  list
[文本1 list，文本2 list]
'''
'''卡方分布选feature'''
def get_chi(txt_dic):
    class_dic = {}
    # classes = len(txt_dic)
    # key - word  value - 所有类下word出现的文档数
    word_dic = {}
    class_type_list = txt_dic.keys()
    n = 0
    for class_type, txt_list in  txt_dic.items():
        print class_type
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
        
    word_count = len(word_dic)
    count = 1
    for w, wc in word_dic.items():
        print '%s out of %s' % (count, word_count)
        count += 1
        # wc表示出现w的文档数
        chi_max = -1
        ct = None
        first = True
        for class_type in class_type_list:
            txt_count = float(class_dic[class_type][0])
            # 每个词在class_type类出现的文档数
            tw_dic = class_dic[class_type][1]
            a = 0 if w not in tw_dic else float(tw_dic[w])
            c = txt_count - a
            b = wc - a
            d = (n - txt_count) - b
            if a == 0:
                a = 0.001
            if b == 0:
                b = 0.001
            if d == 0:
                d = 0.001
            if c == 0:
                c = 0.001
            chi = (n * (a * d - c * b) * (a * d - c * b)) / ((a + c) * (b + d) * (a + b) * (c + d))
            if first:
                first = False
                chi_max = chi
                ct = class_type
            else:
                if chi > chi_max:
                    chi_max = chi
                    ct = class_type
#         print w,mi_max,ct
        word_dic[w] = [chi_max, ct]
    return word_dic

'''
industry_dic = {}
for job_raw in fileinput.input(["/home/xuelong/ipin/company_industry/ttttt"]):
    job_raw = job_raw.replace('\n', '')
    job_f = job_raw.split()
    comp = job_f[0]
    industry = job_f[1]
    if True:
        if industry not in industry_dic:
            industry_dic[industry] = []
            print industry
        industry_dic[industry].append(job_f[2:])
fileinput.close()

# key - word   value - 
word_dic = get_chi(industry_dic)
'''
def featureSelection():
    FS = pickle.load(open('sample2Dict.pk'))     # a dictionary where label is the key and a list of sample texts is the value
    result = get_chi(FS)
    printer(result)
    
def is_alphabet(uchar):
        """判断一个unicode是否是英文字母"""
        if (uchar >= u'\u0041' and uchar<=u'\u005a') or (uchar >= u'\u0061' and uchar<=u'\u007a'):
                return True
        else:
                return False
            
def is_chinese(uchar):
        """判断一个unicode是否是汉字"""
        if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
                return True
        else:
                return False

def printer(word_dic):
    Label = pickle.load(open('hierPos_Dict.pk'))
    selectedFeature = open('selected_Feature.pk', 'w')
    CHI = {}            # store the Chi of each feature by the labels
    Feature = []        # save the selected features
    for wd in word_dic.keys():
        label = word_dic[wd][1]
        if not CHI.has_key(label):
            CHI[label] = [(wd, word_dic[wd][0])]
        else:
            CHI[label].append((wd, word_dic[wd][0]))
    for k in CHI.keys():
        fileName = Label[k]
        print fileName
        outFile = open(('featureSelection/' + fileName), 'w')      
        sort_Dist = sorted(CHI[k], key = lambda d: d[1], reverse = True)
        count = 0
        for i in xrange(len(sort_Dist)):
            outFile.write('%f   %s\n' % (sort_Dist[i][1], sort_Dist[i][0]))
#             if sort_Dist[i][1] > 800:           # select the feature if the chi value is greater than 100
#                 Feature.append((sort_Dist[i][0], sort_Dist[i][1]))
            if count < 50:                                              # select the top 50 non-english features
                tmp = unicode(sort_Dist[i][0], 'utf8')
                allEng = True       # see if the word is completely english
                for character in tmp:
                    if is_chinese(character):
                        allEng = False
                        break
                if not allEng and (sort_Dist[i][0] not in Feature) and len(sort_Dist[i][0]) > 3:        # eliminate the english and single characters
                    print sort_Dist[i][0]
                    Feature.append((sort_Dist[i][0], sort_Dist[i][1]))
                    count += 1
                
    sort_Feature = sorted(Feature, key = lambda d: d[1], reverse = True)
    num_of_feature = len(Feature)
    outPut = open('selectedFeature', 'w')
    print len(sort_Feature)
    for i in xrange(num_of_feature):
        outPut.write('%f   %s\n' % (sort_Feature[i][1], sort_Feature[i][0]))
    pickle.dump(sort_Feature, selectedFeature)
        
        
if __name__ == '__main__':
#     featureSelection()



