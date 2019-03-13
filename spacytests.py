"""This example shows how to navigate the parse tree including subtrees
attached to a word.

Based on issue #252:
"In the documents and tutorials the main thing I haven't found is
examples on how to break sentences down into small sub thoughts/chunks. The
noun_chunks is handy, but having examples on using the token.head to find small
(near-complete) sentence chunks would be neat. Lets take the example sentence:
"displaCy uses CSS and JavaScript to show you how computers understand language"

This sentence has two main parts (XCOMP & CCOMP) according to the breakdown:
[displaCy] uses CSS and Javascript [to + show]
show you how computers understand [language]

I'm assuming that we can use the token.head to build these groups."

Compatible with: spaCy v2.0.0+
"""
from __future__ import unicode_literals, print_function

import plac
import spacy
from nltk import Tree


@plac.annotations(
    model=("Model to load", "positional", None, str))
def main(model='en_core_web_sm'):
    nlp = spacy.load(model)
    print("Loaded model '%s'" % model)

    doc = nlp("displaCy uses CSS and JavaScript to show you how computers "
               "understand language")

    # The easiest way is to find the head of the subtree you want, and then use
    # the `.subtree`, `.children`, `.lefts` and `.rights` iterators. `.subtree`
    # is the one that does what you're asking for most directly:
    for word in doc:
        if word.dep_ in ('xcomp', 'ccomp'):
            print(''.join(w.text_with_ws for w in word.subtree))

    # It'd probably be better for `word.subtree` to return a `Span` object
    # instead of a generator over the tokens. If you want the `Span` you can
    # get it via the `.right_edge` and `.left_edge` properties. The `Span`
    # object is nice because you can easily get a vector, merge it, etc.
    for word in doc:
        if word.dep_ in ('xcomp', 'ccomp'):
            subtree_span = doc[word.left_edge.i : word.right_edge.i + 1]
            print(subtree_span.text, '|', subtree_span.root.text)

    # You might also want to select a head, and then select a start and end
    # position by walking along its children. You could then take the
    # `.left_edge` and `.right_edge` of those tokens, and use it to calculate
    # a span.


def nltk_spacy_tree(doc):
    """
    Visualize the SpaCy dependency tree with nltk.tree
    """

    def token_format(token):
        return "_".join([token.orth_, token.tag_, token.dep_])

    def to_nltk_tree(node):
        if node.n_lefts + node.n_rights > 0:
            return Tree(token_format(node),
                       [to_nltk_tree(child)
                        for child in node.children]
                   )
        else:
            return token_format(node)

    tree = [to_nltk_tree(sent.root) for sent in doc.sents]
    # The first item in the list is the full tree
    tree[0].draw()



if __name__ == '__main__':
    nlp = spacy.load('en_core_web_sm')
    sent = 'A plough comprising left- and right-facing plough bodies, each of the left- and right-facing plough bodies comprising.'+\
    ' a mould board;' +\
    'a ploughshare that forms a leading edge of a respective one of the left- and right-facing plough bodies, the leading edge configured to lie in a working position substantially parallel to a soil surface of an area being ploughed; and'+\
    'a wearing-part arrangement for the leading edge provided on the ploughshare, the wearing-part arrangement comprising a plough point configured to be releasably attached to the ploughshare, the plough point having a pointed front portion,'+\
    'wherein at least the front portion is mirror-symmetrical around a longitudinal axis of the plough point and has a first oblique face and a second oblique face diverging in a direction of a socket on the plough point and merging with a first side edge surface and a second side edge surface,'+\
    'wherein the first oblique face is bounded by a first cutting edge, and the second oblique face is bounded by a second cutting edge,'
    doc = nlp(sent)
    nltk_spacy_tree(doc)

    # plac.call(main)

    # Expected output:
    # to show you how computers understand language
    # how computers understand language
    # to show you how computers understand language | show
    # how computers understand language | understand



