# -*- coding: utf-8 -*-
from time import time
from lxml import etree
import claims
import os

class applicationTreeBuilder(etree.TreeBuilder):

    def __init__(self):
        super().__init__()

    def start(self, tag, attributes):
        super().start(tag, attributes)

    def data(self, data):
        super().data(data)

    def end(self, tag):
        super().end(tag)

    def close(self):
        return super().close()


# NOte: a claim_text node may contain children, including other claim text nodes
# def process_claim_text(claim_text):
#     if claim_text.text is not None:  # may be None, I think first one in a claim is always None
#         print(claim_text.text)
#     l = list(claim_text)
#     print(claim_text)
#     print(len(l), l)
#     for el in claim_text.iter():
#         if el.text is not None:
#             print(el.text)
#         if el != claim_text:
#             if el.text is not None:
#                 print('element text =', el.text)
#             if el.tag == 'claim-text':
#                 process_claim_text(el)
#             elif el.tag == 'claim-ref':
#                 process_claim_ref(el)
#             else:
#                 print('unknown tag inside claim text:', el.tag)
#                 print(el)


def process_claim_ref(claim_ref):
    ref = claim_ref.get("idref")
    print(ref, '  ,  ', claim_ref.text)


def inspect_Element(el, level=1):
    print(' . ' * level, 'Element:', el, ' tag=', el.tag, ', num children=', len(list(el)))
    if el.text != None:
        print(' . ' * level, 'el text=', el.text)
    if el.tail != None:
        print(' . ' * level, 'el tail=', el.tail)
    for e in el.iter():
        if e != el:
            inspect_Element(e, level + 1)



    # claim number is embedded in the claim tag
    #      e.g., <claim id="CLM-00002" num="00002">
    # A claim also has one or more <claim-text> elements
    # a claim possibly has a claim ref
    #      e.g., <claim-ref idref="CLM-00001">claim 1</claim-ref>

    # for el in claim.iter(): # first element is the CLAIM tag itself
    #   print('element tag=',el.tag)
    #   if el.text is not None:
    #     print('element text =', el.text)
    #
    #   if el.tag == 'claim-text':
    #     process_claim_text(el)
    #   elif el.tag == 'claim-ref':
    #     process_claim_ref(el)
    #   else:
    #     print('unknown tag ',el.tag)
    #     print('has children:',list(el))

    # for el in claim.iter(): # first element is the CLAIM tag itself
    #   print('element=',el.tag)
    #   if el.text is not None:
    #     print('element text =', el.text)
    #
    #   if el.tag == 'claim-text':
    #     process_claim_text(el)
    #   elif el.tag == 'claim-ref':
    #     process_claim_ref(el)


# Extract pieces of claim text from parse tree element.
# Can return None if the purported claim is actually an instruction, eg, to cancel claims
# Can return None if there is a parse error of some kind
# claim is an lxml.etree._Element
def create_claim_from_XML(claim_xml_element):
    claim_number_string = claim_xml_element.get("num")

    # get parents if any
    parent_claims_strings = []
    for p in claim_xml_element.iter("claim-ref"):
        parent_claim_text = p.get("idref")
        parent_claims_strings.append(parent_claim_text)

    # print("-- processing claim #", claim_number_string)
    claimtext2 = ''
    claimtextList = []
    for el in claim_xml_element.iter():
        claimtext2 += '\n'
        # print('Element:', el, ' tag=', el.tag, ', num children=', len(list(el)))
        if el.text != None:
            element_text = el.text
            # if element_text != '\n':
            if len(element_text.strip()) > 0:
                #delete this diaghostic line
                # if len(element_text.strip()) == 0:
                #     print("element_text %s of claim is empty in claim %s" % (element_text, claimtext2))
                #     print('len=',len(element_text))
                #     for c in element_text:
                #         print('code=',ord(c))
                # assert len(element_text.strip()) > 0, "element_text %s of claim is empty in claim %s" % (element_text,claimtext2)
                element_text = element_text.strip()
                claimtext2 += element_text
                claimtextList.append(element_text)
        if el.tail != None:
            element_text = el.tail

            # if element_text != '\n':
            if len(element_text.strip()) > 0:
                # assert len(element_text) > 0, "element_text of claim is empty"
                element_text = element_text.strip()
                claimtext2 += element_text
                claimtextList.append(element_text)
            # print(len(element_text), 'chars in el text=', element_text)
            # if len(element_text) == 1:
            #     print('char code=', ord(element_text))
    # print("-------- End claim #", claim_number_string)
    # claimtext2 = claimtext2.strip()

    # some application claims are not actually claims
    # for example, a claim might be an isntructionto amend claims, such as:
    #       '1 - 10, (canceled)'
    # It seems the claim amendment process can create wierd 'non-claims'
    # for example, one app has newly added claim 17, but teh XML file has two versions:17 and 17-1
    # As far as I can tell there's no reason for teh claim 17-1, so skip it
    if not claim_number_string.isdigit():
        print(claim_number_string,' is not a number')
        print(claimtextList)
        return None
    else:
        new_claim = claims.create_claim_from_text(claimtextList, claim_number_string, parent_claims_strings)
        return new_claim


def process_all_claims(app_or_patent_num, typeOfPatent, root):
    print(' ================ patent #{} ================ '.format(app_or_patent_num))
    for claimXML in root.iter("claim"):
        claim = create_claim_from_XML(claimXML)
        if claim is not None:
            claim.process_claim() # should move this into the claim's __init__ method
        # claim may be None

        # if isinstance(claim.tag, str):  # or 'str' in Python 3
        #   print("CLAIM>%s - (%s) %d<" % (claim.tag, claim.text, len(claim.text) if claim.text is not None else -1))
        # else:
        #   print("CLAIM SPECIAL: %s - %s" % (claim, claim.text))


def getApplicationNumber(root):
    pubNumberString = root.get("file")  # eg, US20180317366A1-20181108.XML
    pubNumber = pubNumberString.split("-")[0]  # eg, US20180317366A1
    return pubNumber

def getPatentNumber(root):
    pubNumberString = root.get("file")  # eg, US20180317366A1-20181108.XML
    pubNumber = pubNumberString.split("-")[0]  # eg, US20180317366A1
    return pubNumber


def process_app(app):
    appNum = getApplicationNumber(app)
    # print()
    # print('==================================================================================')
    # print()
    # print('processing appNum=', appNum)
    process_all_claims(appNum, app)

def getTypeOfPatent(patent):
    for e in patent.iter("application-reference"):
        t = e.get("appl-type")
        return t # dont want to iterate anyway - only one appl-type node in a tree


#not perfect, because some reissues are design patents
def is_utility_patent(typeOfPatent):
    if typeOfPatent == 'utility':
        return True
    # if typeOfPatent == 'reissue':
    #     return  True
    return False

# for diagnostic only
def     filterInterestingTypesOfPatents(typeOfPatent):
    if typeOfPatent == 'utility':
        return
    if typeOfPatent == 'design':
        return
    if typeOfPatent == 'plant':
        return
    if typeOfPatent == 'reissue':
        return
    print('unknown type of patent=',typeOfPatent)


# should return a value to let you know it processed successfully
def process_patent(patent):
    patentNum = getPatentNumber(patent)
    typeOfPatent = getTypeOfPatent(patent)
    filterInterestingTypesOfPatents(typeOfPatent)
    # dont want to process design orplant patents
    # Also note: design patents always have one vacuous claim (unnumbered)
    if is_utility_patent(typeOfPatent):
    # if patents.is_utility_patent(patentNum):
        process_all_claims(patentNum, typeOfPatent, patent)



def processAllApps(allAppsTree):
    appsProcessed = 0
    for app in allAppsTree.iter("us-patent-application"):
        process_app(app)
        appsProcessed += 1
        if appsProcessed % 1000 == 0:
            print(appsProcessed,' applications processed')
    return appsProcessed

def processAllPatents(allPatentsTree):
    patentsProcessed = 0
    for app in allPatentsTree.iter("us-patent-grant"):
        process_patent(app)
        patentsProcessed += 1
        if patentsProcessed % 1000 == 0:
            print(patentsProcessed,' patents processed')
    return patentsProcessed


# should allow this to check whether a file is patent or application, rather than passing parameter
def processPatentOrApp(inputFileName, isPatent):
    # global appsProcessed
    start_time = time()
    f = open(inputFileName, 'rU')
    # parser = etree.XMLParser(resolve_entities=False, target=applicationTreeBuilder())
    parser = etree.XMLParser(resolve_entities=False)
    allAppsTree = etree.parse(f, parser)
    # print('result tag=', documentTree.tag) # the root's tag is us-patent-application
    # root = documentTree
    elapsed_time = time() - start_time
    print('parsing took ', elapsed_time, ' seconds')
    if isPatent:
        numProcessed = processAllPatents(allAppsTree)
        print('%d patents processed' % numProcessed)
    else:
        numProcessed = processAllApps(allAppsTree)
        print('%d applications processed' % numProcessed)

# process all 'single root' files - ie the files that have been convereted and are ready to XML parse
def processAllInFolder(folderPath, isPatent):
    for single_root_file in os.listdir(folderPath):
        if single_root_file.endswith("_SR.xml"):
            print(single_root_file)
            singleRootFilePath = os.path.join(folderPath, single_root_file)
            processPatentOrApp(singleRootFilePath, isPatent)


if __name__ == "__main__":
    # main(argv[1:])
    # main(["--path", "/media/alderucci/Data/patent data/ipa181108.xml"])
    # main(["--file", "/media/alderucci/Data/patent data/ipa181108_SR.xml"])

    # file name of a file containing XML for a single patent application
    # inputFileName = "ipa181108/US20180317366A1.txt"

    dataDirectory = "patents"
    isPatent = True # will be given patents not applications
    processAllInFolder(dataDirectory, isPatent)

    # start_time = time()
    # inputFileName = "/media/alderucci/Data/patent data/ipg181113_SR.xml"
    #
    # # main(["--file", outputFileName])
    #
    # processPatentOrApp(inputFileName, isPatent = True)
    # elapsed_time = time() - start_time
    # print('total elapsed program time:', elapsed_time, ' seconds')

    print('Program complete.' )