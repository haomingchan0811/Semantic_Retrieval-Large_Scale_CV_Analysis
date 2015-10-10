#start
import pdb, sys, numpy as np, pickle, multiprocessing as mp
sys.path.append('python-emd-master')
from emd import emd

'''Edited and Annotated by Haoming Chen@iPIN on August, 2015'''

# load_file = sys.argv[1]
# save_file = sys.argv[2]
load_file = 'vectors.pk'


''' 
# X:             w2v vectors matrix, iTH column is the iTH document's w2v vectors matrix
# BOW_X:   BOW(word frequency) vectors matrix, iTH column is the iTH document's BOW vectors matrix
# y:             record the iTH document's label index in C (Starting from 1)
# C:             labels in the documents
# words:     store the documents without repeating words
'''
with open(load_file) as f:
    [X, BOW_X, y, C, words] = pickle.load(f)
n = np.shape(X)
n = n[0]                                                # number of documents 
# D = np.zeros((n,n)) #???
for i in xrange(n):
    bow_i = BOW_X[i]                            # the BOW vector matrix of the iTH document
    bow_i = bow_i / np.sum(bow_i)        # calculate the word frequency of each word in the document
    bow_i = bow_i.tolist()                       # transform into List type
    BOW_X[i] = bow_i                            
    X_i = X[i].T                                       # the transpose if the iTH document's w2v vectors matrix, now each row represents a word's w2v vector 
    X_i = X_i.tolist()                                # transform into List type
    X[i] = X_i                                      

def distance(x1,x2):                            # Euclidian distance between two word vectors 
    return np.sqrt(np.sum((np.array(x1) - np.array(x2))**2))

def get_wmd(ix):                                 # calculate the WMD distance between documents
    print '***', ix
    n = np.shape(X)
    n = n[0]                                            # number of documents 
    Di = np.zeros((1,n))                          # (1 x NoOfDocs) matrix
    i = ix
    print '%d out of %d' % (i, n)
    for j in xrange(i):
        print '***'
        print 'X[i] Size = ', np.shape(X[i])
        print 'X[j] Size = ', np.shape(X[j])
        print 'BOW_X[i] Size = ', np.shape(BOW_X[i])
        print 'BOW_X[j] Size = ', np.shape(BOW_X[j])
        Di[0,j] = emd((X[i], BOW_X[i]), (X[j], BOW_X[j]), distance)     # calculate the EMD of two documents
    print Di
    return Di 

def main():
    n = np.shape(X)
    n = n[0]                                             # number of documents 
    pool = mp.Pool(processes=1)           # multiprocess

    pool_outputs = pool.map(get_wmd, list(range(n)))
    pool.close()
    pool.join()

    WMD_D = np.zeros((n,n))                  # WMD between every two documents
    for i in xrange(n):
        WMD_D[:,i] = pool_outputs[i]        # document distance between the iTH document and others
        
    print 
    print WMD_D

#     with open(save_file, 'w') as f:          # save the WMD matrix as pickle
#         pickle.dump(WMD_D, f)

if __name__ == "__main__":
    main()




