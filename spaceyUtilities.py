import spacy
from spacy import displacy


def displayDependencyTree(doc):
    displacy.serve(doc, style='dep')  # http://localhost:5000


def get_root(doc):
    for tok in doc:
        if tok.dep_ == 'ROOT':            return tok
    return None # seriosu error - no root


def _print_tree(r, level):
    print('_'*(level*3), r.text, r.dep_, r.pos_, r.tag_, r.i)
    for c in r.children:
        _print_tree(c, level+1)

def process_nouns(doc):
    for chunk in doc.noun_chunks:
        print("'{chunk.text}', base={chunk.root.text}, dep={chunk.root.dep_}, child of '{chunk.root.head.text}'")

def print_tree(doc):
    r = get_root(doc)
    _print_tree(r, 0)

def print_basic_dependencies(doc):
    print()
    print(':::dependency :::')
    for tok in doc:
        print('{}({}-{}, {}-{})'.format(tok.dep_, tok.head.text, tok.head.i, tok.text, tok.i))



if __name__ == "__main__":


    # Note: don't want to load this more than once
    nlp = spacy.load('en_core_web_sm')


    textToParse = "It is a plough comprising left- and right-facing plough bodies, in which each of the left- and right-facing plough bodies comprises:"
    doc = nlp(textToParse)

    print_tree(doc)


    print()
    print(':: nouns ::')
    process_nouns(doc)

