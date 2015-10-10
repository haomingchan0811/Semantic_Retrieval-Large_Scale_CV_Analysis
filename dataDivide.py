# -*- coding: utf-8 -*-
#!/usr/bin/python

import os
import sys
import string
import jieba
reload(string)
reload(os)
reload(sys)
sys.setdefaultencoding('utf-8')

'''This module is used to divide the big data file into several parts as WMD algorithm has a Memory Leak Problem'''

def main():
    infile = open('src/PartOfPos/Ind_Internet.short', 'r')
    path = '/home/haoming/workspace/POSITION/Position/src/PartOfPos/'
    stop = 0
    i = 0
    filename = (path + '00%d') % i
    out = open(filename, 'w')
    i += 1
    itemCount = 0   # count the number of job records that have been iterated
    prev = ''             # record the cv id of the last job record
    while not stop:
        print itemCount
        nextLine = infile.readline()
        if nextLine == '':
            stop = 1
        else:
            cv_id, job_item, pos, start, end = nextLine.split('\x01', 4)
            itemCount += 1
            if itemCount > 60000:
                if cv_id != prev:
                    out.close()
                    filename = (path + '00%d') % i
                    out = open(filename, 'w')
                    print '-------------%s----------------' % filename
                    i += 1
                    itemCount = 0
                    out.write(nextLine)
                else:
                    out.write(nextLine)
            else:
                out.write(nextLine)
            prev = cv_id
                                                                                                                                                                               
if __name__ == '__main__':
    main()
    