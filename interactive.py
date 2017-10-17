import numpy as np
from keras.models import load_model
from nltk.tokenize import word_tokenize
import argparse
from process_data import find_ngrams, load_pickle, lower_list, load_kv_dataset, vectorize_kv

parser = argparse.ArgumentParser(description='')
parser.add_argument('-m', '--model',
                    default='demo_model_memnn_kv.h5',
                    help='saved keras model')
parser.add_argument('--max_mem_len',
                    default=4,
                    help='max the number of words in one memory')
parser.add_argument('--max_mem_size',
                    default=15,
                    help='max the number of memories related one episode')
parser.add_argument('--max_query_len',
                    default=16,
                    help='max the number of words in question')
args = parser.parse_args()

print(args)
max_mem_len = args.max_mem_len
max_mem_size = args.max_mem_size
max_query_len = args.max_query_len

print('load data...')
    
model = load_model(args.model)

vocab = load_pickle('mov_vocab.pickle')
w2i = load_pickle('mov_w2i.pickle')
i2w = load_pickle('mov_i2w.pickle')
kv_pairs = load_pickle('mov_kv_pairs.pickle')
stopwords = load_pickle('mov_stopwords.pickle')

def predict(q):
    # tokenize a question
    q_tokens = word_tokenize(q)
    q_tokens = lower_list(q_tokens)
    q_tokens = find_ngrams(vocab, q_tokens, 100000)
    print('q_tokens:', q_tokens)

    # vectorize a question
    vec_q = [w2i[w] for w in q_tokens if w in w2i]
    q_pad_len = max(0, max_query_len - len(vec_q))
    vec_q += [0] * q_pad_len
    vec_q = np.array(vec_q)
    vec_q = np.reshape(vec_q, (1, len(vec_q)))
    # print('vec_q:', vec_q)

    # get related kv and vectorize
    data_k, data_v = load_kv_dataset([(None,q_tokens,None)], kv_pairs, stopwords)
    vec_k = vectorize_kv(data_k, max_mem_len, max_mem_size, w2i)
    vec_v = vectorize_kv(data_v, max_mem_len, max_mem_size, w2i)

    int_predict = model.predict([vec_k, vec_v, vec_q], batch_size=1, verbose=0)     
    # print('q:',q)
    print('A:', i2w[np.argmax(int_predict[0])])

while True:
    q = input("Question: ")
    if q != '':
        predict(q)
