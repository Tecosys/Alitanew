import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from Alexa import alexa_bot
from sklearn.model_selection import train_test_split
from ...utils.string_utils import *


class SClassifier:
    def __init__(self, model_path='./Alexa/utils/ham_spam_classify/classify_model.csv') -> None:
        self.model_path = model_path
        self.cv = None
        self.X = None
        self.Y = None
        
    async def prepare_text(self, text):
        return await prepare_for_classification(text)
        
    def load_model(self):
        df = pd.read_csv(self.model_path, encoding="latin-1", low_memory=False)
        df['label'] = df['type'].map({'ham': 0, 'spam': 1})
        X = df['text']
        Y = df['label']
        self.X = X
        self.Y = Y
        self.df = df
    
    def cv_and_train(self):
        X = self.X
        Y = self.Y
        cv = CountVectorizer()
        X = cv.fit_transform(X) 
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=42)
        clf = MultinomialNB()
        clf.fit(X_train,y_train)
        clf.score(X_test,y_test)
        self.cv = cv
        self.clf = clf
    
    @alexa_bot.run_in_exc
    def predict(self, text):
        cv = self.cv
        clf = self.clf
        if isinstance(text, str):
            text = [text]
        vect = cv.transform(text).toarray()
        ham_per, spam_per = clf.predict_proba(vect)[0]
        ham_per = round(ham_per * 100, 2)
        spam_per = round(spam_per * 100, 2)
        return clf.predict(vect)[0] != 0, ham_per, spam_per