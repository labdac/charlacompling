# -*- coding: utf-8 -*-

from functools import reduce
from string import punctuation
import nltk
try:
    nltk.data.find('stopwords')
except LookupError:
    nltk.download('stopwords')
from nltk.corpus import stopwords as nltk_stopwords
from gensim.utils import deaccent
from gensim.models import Phrases
from gensim.models import Word2Vec as w2v
import os
from multiprocessing import Pool
from itertools import chain
from functools import partial

stopwords = nltk_stopwords.words('spanish')
stopwords.extend(['para'])

non_words = list(punctuation)
non_words.extend(['¡','¿','"','(',')'])
non_words.extend(map(str,range(10)))

def tokenize_(string,_additional_stop_words=[]):
    text = "".join([w for w in string if w not in non_words])
    text = deaccent(text).split(' ')
    text = map(lambda x: x.lower().strip(), text)
    text = filter(lambda x: x not in stopwords and x not in _additional_stop_words, text)
    text = [*filter(lambda x: len(x) > 1, text)]
    if text == None:
        return []
    return text

def tokenize(string,additional_stop_words=[]):
    strings = string.replace('\n', '.').split(".")
    return [*filter(lambda x: len(x)>0, map(partial(tokenize_,_additional_stop_words=additional_stop_words),strings))]

def flatten(lists):
    return [*chain.from_iterable(lists)]

def train_model(text, filename, phrases=True, workers=8, window=3, overwrite=False):
    if os.path.exists(filename) and not overwrite:
        return w2v.load(filename)
    pool = Pool(workers)
    tokens = pool.map(tokenize, text)
    cs = flatten(tokens)
    if phrases:
        sentences_phrases = Phrases(cs)
        sentences = sentences_phrases[cs]
    else:
        sentences = cs
    model_titulo = w2v(sentences,workers=workers,window=window,min_count=1,size=300)
    model_titulo.save(filename)
    return model_titulo

def visualizar_embedding(X,y,palabras,title, dynamic=True):
    fig, ax1 = plt.subplots(figsize=(8,8))
    sp = ax1.scatter(X, y)
    
    # Los ticks no tienen sentido
    ax1.tick_params(
        axis='both',
        which='both', 
        right='off',
        left='off',
        bottom='off',
        top='off',
        labelleft='off',
        labelbottom='off')
    ax1.set_title(title)
    
    if dynamic == False:
        # Si son muchos seguro se vea horrible
        for i, txt in enumerate(palabras):
            ax.annotate(txt, (X[i],y[i]))
    else:
        annot = ax1.annotate("", xy=(0,0), xytext=(10,10),textcoords="offset points",
                                bbox=dict(boxstyle="round", fc="w"),
                                arrowprops=dict(arrowstyle="->"))
        annot.set_visible(False)

        def update_annot(ind):
            pos = sp.get_offsets()[ind["ind"][0]]
            annot.xy = pos
            text = str(palabras[ind["ind"][0]])
            annot.set_text(text)

        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax1:
                cont, ind = sp.contains(event)
                if cont:
                    update_annot(ind)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", hover)

    plt.show()

def tsne_w2v(w2v_model):
    tsne = TSNE(n_components=2)
    points = tsne.fit_transform(w2v_model[w2v_model.wv.vocab][:,:])

    palabras = list(w2v_model.wv.vocab.keys())
    X = points[:, 0]
    y = points[:, 1]
    return (X,y,palabras)
