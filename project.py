import csv
import faiss
from faiss import write_index

from gensim.corpora import Dictionary
from gensim.models import LdaModel
from gensim.parsing.preprocessing import STOPWORDS
from gensim.utils import simple_preprocess

import matplotlib.pyplot as plt
import nltk
from nltk.stem import WordNetLemmatizer

import numpy as np
import pandas as pd
import seaborn as sns

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import cross_val_score, train_test_split

from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

import spacy
import torch
from torch.utils.data import TensorDataset, DataLoader, random_split

from transformers import (
    pipeline,
    BertModel,
    BertTokenizer,
    AutoTokenizer,
    AutoModel,
    AutoModelForSequenceClassification
)

from torch.optim import AdamW

#import whisper
#from wordcloud import WordCloud

print('a')