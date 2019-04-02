# -*- coding: utf-8 -*-
import spacy
from spacy import displacy
import re
import sys
import spaceyUtilities as spu

# don't want to load this more than once
nlp = spacy.load('en_core_web_sm')
print('SPACEY ENGLISH LOADED')

# Returns the claim number and separator in the first element of claim text list
# returns None if first element doesnt have the claim number and separator
def firstElementClaimNumberAndSeparator(claimtextList):
    firstPart = claimtextList[0]
    pattern = r'[0-9]+\.'
    # re.match will match the string at the START, re.search matches anywhere in string
    matches = re.match(pattern, firstPart)
    if matches:
        # print(matches.groups())
        matchedClaimNumberAndPeriod = matches.group(0) # group 0 is entire matched pattern
        return matchedClaimNumberAndPeriod
    else:
        return None


#can return None if there are parsing errors
# Note: Make sure not to call this for any design patent claim.
#   Design patents always have one vacuous claim which is unnumbered
def remove_claim_number(claimtextList):

    removed_claim_number = claimtextList[0]

    # handle the typical case:
    # first element is just a number,
    # second element starts with the period separator (which follows the claim number).
    # for example "6. The method ..." is stored as ['6', '. The method..', ... ]
    if removed_claim_number.isdigit() and (len(claimtextList) > 1) and claimtextList[1][0] == '.':
        # assumption: first element of list is the number, and the second element of the list starts with a period
        #
        # print('list:',claimtextList)
        first_char_of_first_elem = claimtextList[1][0]

        claimtextList.pop(0)
        claimtextList[0] = claimtextList[0][1:] # skip first char
        claimtextList[0] = claimtextList[0].strip()
        return claimtextList, removed_claim_number

    else:
        # print('claim list:',claimtextList)
        # print('claimtextList[0]=',claimtextList[0])

        #does the first element contain the claim number and separator and initial text of claim?
        # eg "6. The method ..." is stored as ['6. The method..', ... ]

        claimNumndSep = firstElementClaimNumberAndSeparator(claimtextList)
        if claimNumndSep is not None:
            # remove claim number and separator
            removed_claim_number = claimNumndSep[:-1] # assumes just one period follows number
            claimtextList[0] = claimtextList[0][len(claimNumndSep):]
            claimtextList[0] = claimtextList[0].strip()
            if len(claimtextList[0]) == 0: #if now empty, remove it
                claimtextList.pop(0)
            return claimtextList, removed_claim_number
        # else first element doesnt contain the claim number and separator
        else:
            return None, None


        # saving this dead unreachable code just in case
        if claimtextList[0].isdigit(): # removed_claim_number still the claim number
            claimtextList.pop(0)
        else:
            parts = claimtextList[0].split('.')  # assume the separator is a period
            if parts[0].isdigit():  # assume we got a good claim number
                removed_claim_number = parts[0]
                num_chars_to_delete = claimtextList[0].find(".")
                print(claimtextList)

                claimtextList[0] = claimtextList[0][num_chars_to_delete:]
                print(claimtextList)
                print(removed_claim_number)

        first_char_of_first_elem = claimtextList[1][0]

        #sometimes a typo means a character besides a period ends the claim number
        if first_char_of_first_elem == '.' \
                or first_char_of_first_elem == ')' \
                or first_char_of_first_elem == '-' \
                or first_char_of_first_elem == ':':
            claimtextList[0] = claimtextList[0][1:] # skip first char in (what was previously the) second element
            claimtextList[0] = claimtextList[0].strip()

        # sometimes the XML doesnt separate the claim number  as one element and teh period n the next element
        # instead the first element has teh claim number and its separator (eg a period)
        # For example, the first element may be "6. The ..."
        else:
            parts = claimtextList[0].split('.') # assume the separator is a period
            if parts[0].isdigit(): # assume we got a good claim number
                removed_claim_number = parts[0]
                num_chars_to_delete = claimtextList[0].find(".")
                print(claimtextList)

                claimtextList[0] = claimtextList[0][num_chars_to_delete:]
                print(claimtextList)
                print(removed_claim_number)
                print(first_char_of_first_elem)

            else:
                return None,None
    # print('list:',claimtextList)
    # print('removed claim=',removed_claim_number)
    # print('first_char=',first_char_of_first_elem)

        return claimtextList, removed_claim_number

# can return None if parse error
def cleanClaimText(claimtextList, claim_number_string):
    # print('claim number should be:',claim_number_string)
    claimtextList, removed_claim_number = remove_claim_number(claimtextList)
    if claimtextList is None:
        return None
    try:
        true_claim_num = int(claim_number_string)
    except ValueError as error:
        print(error)
        print("can't convert claim number %s to integer" % claim_number_string)
        print(claimtextList)
    # print('true claim #=',true_claim_num)

    extracted_claim_num = int(removed_claim_number)
    # print('extracted claim #=',extracted_claim_num)
    if true_claim_num != extracted_claim_num:
        print('True claim number %d doesnt match extracted claim number %d' % (true_claim_num, extracted_claim_num))
    return claimtextList


# assumes teh string is from teh original XML idref attribute
# eg, 'CLM-00001'
def get_claim_number_from_attribute_string(claim_number_string):
    s = claim_number_string[4:]
    return int(s)

def get_claim_numbers_from_attribute_strings(claims_number_string):
    l = []
    for c in claims_number_string:
        e = get_claim_number_from_attribute_string(c)
        l.append(e)
    return l

# can return None if parse error
# claim_number_string is composed of only digit characters
# TODO check if it is dependent, if so get parent claims
def create_claim_from_text(claimtextList, claim_number_string, reference_claims_strings):
    claimtextList = cleanClaimText(claimtextList, claim_number_string)
    if claimtextList is None:
        return None
    # print('claim list:')
    # for el in claimtextList:
    #     print(el)

    claim_number_as_int = int(claim_number_string)
    reference_claims_as_ints = get_claim_numbers_from_attribute_strings(reference_claims_strings)
    claim = Claim(claimtextList, claim_number_as_int, reference_claims_as_ints)
    return claim



def showTree(sent):

    def __showTree(token):
        sys.stdout.write("{")
        [__showTree(t) for t in token.lefts]
        sys.stdout.write("%s->%s(%s)" % (token, token.dep_, token.tag_))
        [__showTree(t) for t in token.rights]
        sys.stdout.write("}")

    r = sent.root
    return __showTree(r)


def showTree2(sent):

    def __showTree2(token):
        sys.stdout.write("{")
        [__showTree2(t) for t in token.lefts]
        sys.stdout.write("%s->%s(%s)" % (token,token.dep_,token.tag_))
        [__showTree2(t) for t in token.rights]
        sys.stdout.write("}")

    r = sent.root
    return __showTree2(r)


class Claim():
    """
        A claim stores a list of 'components' (strings)
        Also stores a list of its parents, or None is it is an independent claim
        The parents list is a list of claims referred to,
        and may not necessarily indicate the claim is dependent
    """
    def __init__(self, list_of_component_strings, claim_number_as_int, claimReferenceInts=[]):
        super().__init__()
        self.component_strings = list_of_component_strings
        self.claim_number = claim_number_as_int
        self.parent_claims = claimReferenceInts # keep in mind not definitely parents yet
        self.find_start_of_claim_body()

    def find_start_of_claim_body(self):
        # first try the easiest cases

        # EASY CASE: first component ends with 'comprising:' or similar word
        first_component = self.component_strings[0]
        doc = nlp(first_component)


        if len(self.parent_claims) == 0: # no references to other claims, definitely independent claim

            print('First component of claim:')
            print('    ', first_component)

            last_token = doc[-1]
            second_to_last_token = doc[-2]
            if second_to_last_token.text == 'comprising' and last_token.text ==':': # first component ends with 'comprising:'
                print('first ends with comprising:')


        # if len(self.parent_claims) == 0: # no references to other claims, definitely independent claim
        #
        #
        #     print()
        #     print(':::tree:::')
        #     for sent in doc.sents:
        #         showTree(sent)
        #         sys.stdout.flush()
        #
        #     print()
        #     print(':::dependency of first component:::')
        #     for tok in doc:
        #         print('{}({}-{}, {}-{})'.format(tok.dep_, tok.head.text, tok.head.i, tok.text, tok.i))
        # else: # includes reference to another claim, so its a possible dependent claim
        #     print()
        #     print(':::dependency of first component:::')
        #     for tok in doc:
        #         print('{}({}-{}, {}-{})'.format(tok.dep_, tok.head.text, tok.head.i, tok.text, tok.i))

    def is_independent(self):
        return len(self.parent_claims) == 0

    def is_dependent(self):
        return len(self.parent_claims) > 0

    def is_multiple_dependent(self):
        return len(self.parent_claims) > 1

    def has_one_parent(self):
        return len(self.parent_claims) == 1

    def print_claim_components(self):
        for c in self.component_strings:
            print(c)


    def __str__(self):
        s = '\tClaim #{} ({})'.format(self.claim_number, 'Independent' if self.is_independent() else 'dependent')
        s += '\n'
        if self.is_dependent():
            s += '\tParents #{}'.format(self.parent_claims)
            s += '\n'
        s += '\tClaim components:'
        s += '\n'
        for c in self.component_strings:
            s += '\t'+ c + '\n'
        return s


    def __repr__(self):
        return self.__str__()

    # This assumes the XML has been extracted and this is the first processing on the claim object
    #   (which contains just text at this point)
    def process_claim(self):
        # print(str(self))
        # self.do_dependency_test_on_first_component()

        # if self.is_dependent():
        #     self.check_dependent_claim_structure()
        pass


    # does the only component that is simply 'claim xxxx' appear as the second component
    # eg, ['the method of', 'claim 1', ...]
    def check_dependent_claim_structure(self):
        if len(self.component_strings) <= 1:
            print('STRUCTURE ERROR, claim has only ', len(self.component_strings), 'components, > 1 expected')
            print(self)
            return
        else:
            second_component = self.component_strings[1]
            if second_component.startswith('claim ') or second_component.startswith('Claim '):
                pass
            else:
                print('STRUCTURE ERROR, second claim component=', second_component)
                print(self)

    def do_dependency_test_on_first_component(self):
        nlp = spacy.load('en_core_web_sm')
        doc = nlp(self.component_strings[0])
        # displacy.serve(doc, style='dep') # http://localhost:5000
        # print()
        # print(':::dependency tree:::')
        # for token in doc:
        #     print(token.text, token.dep_, token.head.text, token.head.pos_,
        #           [child for child in token.children])
        print()
        print(':::dependency 2:::')
        for tok in doc:
            print('{}({}-{}, {}-{})'.format(tok.dep_, tok.head.text, tok.head.i, tok.text, tok.i))

    def testSpacey(self):
        print(' ------------ spacey test ------------ ')

        nlp = spacy.load('en_core_web_sm')
        for claim_component in self.component_strings:
            print(claim_component)
            doc = nlp(claim_component)
            # displacy.serve(doc, style='dep')

            for sent in doc.sents:
                showTree(sent)
                sys.stdout.flush()

            print()
            print(':::Noun chunks:::')
            for chunk in doc.noun_chunks:
                print('<<{}>> {} ({}) has head:{}'.format(chunk.text, chunk.root.text, chunk.root.dep_,
                      chunk.root.head.text))

            print()
            print(':::dependency tree:::')
            for token in doc:
                print(token.text, token.dep_, token.head.text, token.head.pos_,
                      [child for child in token.children])

            print()
            print(':::dependency 2:::')
            for tok in doc:
                print('{}({}-{}, {}-{})'.format(tok.dep_, tok.head.text, tok.head.i, tok.text, tok.i))

            # Finding a verb with a subject from below — good
            verbs = set()
            for possible_subject in doc:
                if possible_subject.dep == spacy.symbols.nsubj and possible_subject.head.pos == spacy.symbols.VERB:
                    verbs.add(possible_subject.head)
            print(verbs)

            print()
            print('entities')
            for ent in doc.ents:
                print(ent.text, ent.start_char, ent.end_char, ent.label_)

            print()
            print('=================')
            print()
