# -*- coding: utf-8 -*-
#!/usr/bin/python

import gensim, pdb, sys, scipy.io as io, numpy as np, pickle, string
reload(sys)
sys.setdefaultencoding('utf-8')
'''Edited and Annotated by Haoming Chen@iPIN on August, 2015'''

# read datasets line by line
def read_line_by_line(dataset_name,C,model,vec_size):
    # get stop words (except for twitter!)
#     SW = set()
#     for line in open('stop_words.txt'):
#         line = line.strip()
#         if line != '':
#             SW.add(line)
# 
#     stop = list(SW)

    f = open(dataset_name)
    # Initialize: 0-dim array
    if len(C) == 0:
        C = np.array([], dtype=np.object)                           # labels in the documents
    # number of lines in the dataset
    num_lines = sum(1 for line in open(dataset_name))   # number of documents 
    # (1 x num_lines) zeros matrix
    y = np.zeros((num_lines,))                                           # record the iTH document's label index in C (Starting from 1)
    X = np.zeros((num_lines,), dtype=np.object)              # w2v vectors matrix, iTH column is the iTH document's w2v matrix
    Weight_X = np.zeros((num_lines,), dtype=np.object)     # Weight(word frequency+IDF) vectors matrix, iTH column is the iTH document's Weight matrix
    count = 0                                                                      # current iterated document
#     remain = np.zeros((num_lines,), dtype=np.object)  # ???
    the_words = np.zeros((num_lines,), dtype=np.object) # store the documents without repeating words
    
    for line in f:
        print '%d out of %d' % (count+1, num_lines)
        line = line.strip()
        line = line.translate(string.maketrans("",""), string.punctuation)  # remove the punctuation
        T = line.split('\t')
        classID = T[0]
        if classID in C:
            IXC = np.where(C==classID)      # return the indexes of the classID appeared in the C array
            y[count] = IXC[0]+1                    # label index of the countTH document in C: IXC[0] returns the first index, '+1' means the next index (Index starting from 1)
        else:
            C = np.append(C,classID)
            y[count] = len(C)                         # label index of the countTH document in C
            
        W = line.split()                                 # split the words apart
        # store each word's vector in a column, '-1' means neglect the document ID
        F = np.zeros((vec_size,len(W)-1))   
        inner = 0                                         # iterator for the split words
        #(1 x numOfwords) matrix, what for???
#         RC = np.zeros((len(W)-1,), dtype=np.object)    

        # store the split words in order: repeated word will be stored in its first occurrence and then stored as '' afterwards
        word_order = np.zeros((len(W)-1), dtype=np.object)  
        # Weight vector: number of occurrence of each word in the word_order matrix
        bow_x = np.zeros((len(W)-1,))
        for word in W[1:len(W)]:                   # ignore the document ID(W[0])
            word = word.decode('utf-8')
            try:
                test = model[word]                  # w2v embedding word vector
#                 if word in stop:
#                     word_order[inner] = ''
#                     continue
                if word in word_order:
                    IXW = np.where(word_order==word)
                    bow_x[IXW] += 1                 # number of occurrence of the repeated word recorded at its first occurrence position
                    word_order[inner] = ''          # repeated word will be stored as '' for the 2nd or later occurrence 
                else:
                    word_order[inner] = word    # store the word at its first occurrence
                    bow_x[inner] += 1                # number of occurrence of the word 
                    F[:,inner] = model[word]      # load the corresponding w2v word vector into the corresponding column 
            except KeyError, e:
                #print 'Key error: "%s"' % str(e)
                word_order[inner] = ''
            inner = inner + 1
        # eliminate the 0 columns and transpose, now each row is a w2v word vector
        Fs = F.T[~np.all(F.T == 0, axis=1)]                      # F.T: transpose of the F matrix; '~': converse position logical(按位取反);
        word_orders = word_order[word_order != '']     # remove the ''s(representing repeated words)
        bow_xs = bow_x[bow_x != 0]                  # remove the 0s(representing repeated words)
        X[count] = Fs.T                                                    # store the words' vectors matrix of the countTH document
        the_words[count] = word_orders                        # store the non-repeating words in order of the countTH document
        Weight_X[count] = bow_xs                              # store the Weight vectors of the countTH document
        count = count + 1
    return (X,Weight_X,y,C,the_words)

def main():
    # 0. load word2vec model (trained on Google News)
#     model = gensim.models.Word2Vec.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)
    model = gensim.models.word2vec.Word2Vec.load('/home/haoming/workspace/POSITION/Position/word2vec_model/word2vec.model')
    vec_size = 50

    # 1. specify train/test datasets
    # Format: ID'/t'word1 word2 word3, punctuation and extra blank or whatnot is allowed
#     train_dataset = sys.argv[1]              # e.g.: 'twitter.txt'
    train_dataset = 'testWMD.txt'             
#     save_file = sys.argv[2]                     # e.g.: 'twitter.pk'
    save_file = 'vectors.pk'
#     save_file_mat = sys.argv[3]         # e.g.: 'twitter.mat'

    # 2. read document data
    (X,Weight_X,y,C,words)  = read_line_by_line(train_dataset,[],model,vec_size)

    # 3. save pickle of extracted variables
    with open(save_file, 'w') as f:
        pickle.dump([X, Weight_X, y, C, words], f)

    # 4. (optional) save a Matlab .mat file
#     io.savemat(save_file_mat,mdict={'X': X, 'Weight_X': Weight_X, 'y': y, 'C': C, 'words': words})

if __name__ == "__main__":
    main()                                                                                             
