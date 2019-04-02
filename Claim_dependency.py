import spacy


nlpNP = spacy.load('en', disable = ['textcat'])
nlp = spacy.load('en')
nlpL = spacy.load('en', disable=['ner', 'parser'])
nlpL.add_pipe(nlpL.create_pipe('sentencizer'))

StopWordsFile = open("Stopwords", "r")
stopwords= [word.replace("\n","") for word in StopWordsFile]
StopWordsFile.close()


def lemmatize(text):
    # Extracts roots of words
    lemma = " "
    for w in text:
        if(not w.lemma_ in stopwords):
            lemma+= (w.lemma_) + " "
    return lemma

def check_similarity(phrase1, phrase2):
    print(phrase1, phrase2)
    return phrase1.similarity(phrase2)
