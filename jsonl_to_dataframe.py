import pandas as pd
import json
import re
import time
import gensim
from nltk.tokenize import TweetTokenizer

tokenizer = TweetTokenizer(strip_handles=True)


def info(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print('Function', method.__name__, 'time:', round((te -ts)*1000,1), 'ms')
        print()
        return result
    return timed


def strip_non_alphanum(token):
    return re.sub(r'\W+', '', token)


def tokenize(tweet_text, remove_non_alphanum=True, lowercase=False):
    if lowercase:
        tweet_text = tweet_text.lower()
    tokens = tokenizer.tokenize(tweet_text)
    if remove_non_alphanum:
        tokens = [strip_non_alphanum(t) for t in tokens]
    return list(filter(None, tokens))


def get_dataframe_from_jsonl(path):
    data = []
    index = []
    for i, line in enumerate(open(path, 'r')):
        instance = json.loads(line)
        data.append(instance)
        index.append(instance['id'])
    df = pd.DataFrame(data=data, index=index)
    df.sort_index(inplace=True)
    return df


@info
def instances_to_token(path_to_instances, data_dir, file_prefix, fill_na_token='unk'):
    df_instances = get_dataframe_from_jsonl(path_to_instances)
    df_instances.to_pickle(data_dir + file_prefix + '_instances.pickle')
    df_tokens = df_instances.apply(lambda row: tokenize(row['postText'][0]), axis=1)
    df_tokens = pd.DataFrame(df_tokens.values.tolist(), df_tokens.index).add_prefix('token_')
    df_tokens.fillna(fill_na_token, inplace=True)
    df_tokens.to_pickle(data_dir + file_prefix + '_tokens.pickle')
    return df_tokens


def token_to_index(vocab, token, unknown_token='unk'):
    try:
        return vocab[token].index
    except KeyError:
        return vocab[unknown_token].index


@info
def tokens_to_indices(tokens_df, data_dir, file_prefix, vocab):
    indices_df = tokens_df.applymap(lambda t: token_to_index(vocab, t))
    indices_df.to_pickle(data_dir + file_prefix + '_indices.pickle')


def get_vocab_and_pretrained_embedding(path_to_model):
    model = gensim.models.KeyedVectors.load_word2vec_format(path_to_model, binary=True)
    W = model.syn0
    print('model shape:')
    print(W.shape)
    vocab = model.vocab
    return vocab, W


def negate(x):
    return 1-x


@info
def instances_to_labels(path_to_labels, data_dir, file_prefix):
    df_truth = get_dataframe_from_jsonl(path_to_labels)
    df_truth = df_truth.ix[:, 'truthMean'].to_frame()
    df_truth['negTruthMean'] = df_truth.apply(lambda x: negate(x), axis=1)
    df_truth.to_pickle(data_dir + file_prefix + '_labels.pickle')


def main():
    data_dir = '/home/xuri3814/data/clickbait/'
    path_to_instances = data_dir + 'all_instances.jsonl'
    path_to_labels = data_dir + 'all_truth.jsonl'
    file_prefix = 'googlenews300'
    # path_to_model = data_dir + 'googlenews300.bin'
    # df_tokens = instances_to_token(path_to_instances, data_dir, file_prefix)
    # vocab, _ = get_vocab_and_pretrained_embedding(path_to_model)
    # tokens_to_indices(df_tokens, data_dir, file_prefix, vocab)
    instances_to_labels(path_to_labels, data_dir, file_prefix)

if __name__ == '__main__':
    main()
