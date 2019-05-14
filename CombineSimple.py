from claim_tree import *

import re
from gensim.summarization.summarizer import summarize
from gensim.summarization import keywords
import spacy
import requests

#if 'en_core_web_sm' doesn't work, try 'en': check spacy/data to see what the package installed on your machine is called
nlpNP = spacy.load('en_core_web_sm', disable = ['textcat'])
nlp = spacy.load('en_core_web_sm')
nlpL = spacy.load('en_core_web_sm', disable=['ner', 'parser'])
nlpL.add_pipe(nlpL.create_pipe('sentencizer'))
 

StopWordsFile = open("Stopwords", "r")
stopwords= [word.replace("\n","") for word in StopWordsFile]
StopWordsFile.close()

def strip_before(text):
    i = 0
    textList = text.split()
    for w in textList:
        if(w.lower() not in stopwords):
            break
        i+=1
    return textList[i:]

def strip_after(textList):
    i = 0
    last_not_stop = -1
    for w in textList:
        if(w.lower() not in stopwords):
            last_not_stop = i
        i+=1
    return textList[:last_not_stop+1]

def strip(text):
    stripped_b = strip_before(text)
    stripped_a = strip_after(stripped_b)
    return " ".join(stripped_a)

    
def getNounPhrases(doc):
    noun_phrases = [np.text for np in doc.noun_chunks] 
    all_nouns =  list([str(word.text) for word in doc if str(word.pos_)== 'NOUN'])  
    noun_phrases+=all_nouns
    return noun_phrases

def get_noun_chunks(node, graph):
    info = ""       
    claim_ref_p = re.findall(r"(.*)claim|$", nodes[node].info)
    if(len(claim_ref_p)==0):
        info = nodes[node].info.replace("\n", " ")
    else:
        prev_ref = lemmatize(nlpL(str(claim_ref_p[0])))
    prev_ref = nlp(prev_ref)
    number = nodes[node].number
    node_np = getNounPhrases(nlp(nodes[node].info))
    return node_np

def getNouns(node, graph):
    all_np = get_noun_chunks(node, graph)
    final_np = []
    for np in all_np:
        final_np.append(strip(np))
    return final_np

def get_noun_chunks_ancestors(node, graph):
    info_anc = []
    nodes = graph.nodes_dict
    ancestors = graph.find_ancestors(node)
    info = ""       
    claim_ref_p = re.findall(r"(.*)claim|$", nodes[node].info)
    if(len(claim_ref_p)==0):
        info = nodes[node].info.replace("\n", " ")
    else:
        info = str(claim_ref_p[0])
    prev_ref = lemmatize(nlpL(info))
    prev_ref = nlp(prev_ref)
    number = nodes[node].number
    anc_rev = ancestors[::-1]
    node_np = getNouns(nlp(nodes[node].info))
    all_info = {}
    for ancestor in anc_rev:
        prev_ref_np = getNouns(nlp(nodes[ancestor].info))
        info_anc.append(prev_ref_np)
    return info_anc
        

def processAllPatents(allPatentsTree):
    patentsProcessed = 0

    for app in allPatentsTree.iter("us-patent-grant"):
        edges, infos = create_patent_dict(app)
        graph_class = ClaimSet(app)
        patentsProcessed += 1
        if patentsProcessed % 1000 == 0:
            print(patentsProcessed,' patents processed')
        combineInfo(graph_class)
    return (patentsProcessed)


# should allow this to check whether a file is patent or application, rather than passing parameter
def processPatentOrApp(inputFileName, isPatent):
    # global appsProcessed
    start_time = time()
    f = open(inputFileName, 'rU')
    # parser = etree.XMLParser(resolve_entities=False, target=applicationTreeBuilder())
    parser = etree.XMLParser(resolve_entities=False)
    allAppsTree = etree.parse(f, parser)
    elapsed_time = time() - start_time
    print('parsing took ', elapsed_time, ' seconds')
    if isPatent:
        (numProcessed) = processAllPatents(allAppsTree)
        print('%d patents processed' % numProcessed)

def lemmatize(text):
    # Extracts roots of words
    lemma = " "
    for w in text:
        if(not w.lemma_ in stopwords):
            lemma+= re.sub(r"[0-9]+"," ", w.lemma_) + " "
    return lemma

def check_similarity(phrase1, phrase2):
    return phrase1.similarity(phrase2)

def combineInfo(graph):
    combined_info_dict = {}
    nodes = graph.nodes_dict
    for node in nodes:
        ancestors = graph.find_ancestors(node)
        info = ""
        claim_ref_p = re.findall(r"(.*)claim|$", info)
        if(len(claim_ref_p)==0):
            info = node + nodes[node].info.replace("\n", " ")
        else:
            prev_ref = lemmatize(nlpL(str(claim_ref_p[0])))
            prev_ref = nlp(prev_ref)
        number = nodes[node].number
        anc_rev = ancestors[::-1]
        anc_info = ""
        for ancestor in ancestors:
            prev_ref_a = prev_ref_a = re.findall(r"(.*)claim", nodes[ancestor].info.replace("\n", " "))
            #re.split(".claim [0-9]*", nodes[ancestor].info.replace("\n", " "))[-1]
            #print("prev_ref_a:", prev_ref_a)
            i = True
            for p in prev_ref_a:
                prev_ref_a1 = lemmatize(nlpL(p))
                prev_ref_aN = nlp(prev_ref_a1)
                if(check_similarity(prev_ref_aN, prev_ref)==1):
                    i = False
                    anc_info += ("\n" + nodes[ancestor].info.replace(prev_ref_a1, "\n") + " ; ")
            if(i):
                anc_info = "\n" + nodes[ancestor].info + "; " + anc_info#nodes[ancestor].info
        
        
        info += nodes[node].info.replace("\n", " ")
        info = anc_info  + info
        combined_info_dict[number] = info
        print("_________________________________________")
        print("Claim number", number,"\n", info)
        print("_________________________________________")
        #print("Claim number" ,number, "\n", info)
    return combined_info_dict

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
