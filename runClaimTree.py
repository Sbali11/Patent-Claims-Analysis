from claim_tree import *

def processAllPatents(allPatentsTree):
    patentsProcessed = 0
    for app in allPatentsTree.iter("us-patent-grant"):
        create_patent_dict(app)
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
