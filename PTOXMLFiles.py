import os

import re

def insert_line_at_start_of_file(originalfile, line):
    tempFileName = 'newfile.txt'
    with open(originalfile,'r') as f:
        with open(tempFileName,'w') as f2:
            f2.write(line)
            f2.write(f.read())
    os.rename(tempFileName,originalfile)

customRootTag = "PTOXMLFile"
rootStart = "<"+customRootTag +">"
rootEnd = "</"+customRootTag +">"

'''
// A file in the PTO's format is basically multiple concatenated XMLs, and
	// so does not have one root.
	// This should be the first step in the process of using the file.
	//
	// Converts a file from the PTO's format 
	// by making everything in the file fall under a single root.
	// This makes it a proper XML document, so conventional XML processors can handle it.
	//
	// The convertPTOFile() method also removes lines with <?xml and <!DOCTYPE 
'''
def create_single_root_file_from_PTO_file(originalFileName, singleRootFileName):

    inFile = open(originalFileName, 'r')
    outFile = open(singleRootFileName, 'w')

    outFile.write(rootStart)
    outFile.write("\n")

    for line in inFile:
        # print(line)
        if line.startswith("<?xml") or line.startswith("<!DOCTYPE"):
            continue
        outFile.write(line)

    # os.rename(tempFileName, originalFileName)
    outFile.write(rootEnd)
    outFile.write("\n")
    outFile.close()



def processStartAppLine(line):
    pattern = r'file=".*?"'  # .*? is greedy, so it matches the minimal number, that is until the first quotation, not last
    # if re.search(pattern, line):
    #     print("Match!")
    # else:
    #     print("Not a match!")
    # if re.search(p2, line):
    #     print("Match!")
    # else:
    #     print("Not a match!")
    # heading  = r'<h1>TITLE</h1>'
    # z = re.search(r'<.*?>', heading).group()
    # print(z)

    # heading  = '<us-patent-application lang="EN" dtd-version="v4.4 2014-04-03" file="US20180317366A1-20181108.XML" status="PRODUCTION" id="us-patent-application" country="US" date-produced="20181024" date-publ="20181108">'
    z = re.search(pattern, line).group()
    # heading  = 'us-patent-application lang="EN" dtd-version="v4.4 2014-04-03" file="US20180317366A1-20181108.XML" status="PRODUCTION" id="us-patent-application" country="US" date-produced="20181024" date-publ="20181108"'
    # print(z)
    fileName = z.split('"')[1]
    # print(fileName)
    pubNumber = fileName.split('-')[0]
    return pubNumber


def processEndAppLine(line):
    pass
    # print(line)

def splitPTOXMLFileIntoManyFiles(inputFileName, directory, processApps):
    if processApps:
        startAppTag = "<us-patent-application"
        endAppTag = "</us-patent-application"
    else: # patents
        startAppTag = "<us-patent-grant"
        endAppTag = "</us-patent-grant"

    inputFile = open(inputFileName, 'r')
    outputFile = None
    app_index = 0
    for line in inputFile:
        # print(line)
        if line.startswith("<?xml") or line.startswith("<!DOCTYPE"):
            continue
        if line.startswith(startAppTag):
            app_index += 1
            pubNumber = processStartAppLine(line)
            outputFileName = directory + '/' + pubNumber + ".txt"
            # print('writing file',outputFileName)
            outputFile = open(outputFileName, 'w')
            if app_index % 100 == 0:
                print('processing included application #',app_index)

        if not outputFile.closed:
            outputFile.write(line)
        # else:
        #     print('file_index=',file_index)


        if line.startswith(endAppTag):
            processEndAppLine(line)
            outputFile.close()
            # print('closed file_index=',file_index)

    outputFile.close()

    # print first 200 lines
    # lineNumber = 0
    # while lineNumber < 200:
    #     line = inputFile.readline()
    #     print(line)
    #     lineNumber += 1
    # lines = inputFile.readlines()
    # print(len(lines),' lines')
    inputFile.close()

# def makeSingleRootFileFromPTOXMLFile(inputFileName, outputFileName):
#     startAppTag = "<us-patent-application"
#     endAppTag = "</us-patent-application"
#
#     inputFile = open(inputFileName, 'r')
#     outputFile = open(outputFileName, 'w')
#
#
#     for line in inputFile:
#         # print(line)
#         if line.startswith("<?xml") or line.startswith("<!DOCTYPE"):
#             continue
#
#         outputFile.write(line)
#
#
#     outputFile.close()

def unzipPTOFileAndCreateSingleRoot(zippedXMLFile, outputDirectory):
    import zipfile

    with zipfile.ZipFile(zippedXMLFile, "r") as zip_ref:
        unzippedNames = zip_ref.namelist()
        firstUnzippedFileName = unzippedNames[0] # assume there's only one file
        pathToFirstUnzippedFile = os.path.join(outputDirectory, firstUnzippedFileName)
        zip_ref.extractall(path=outputDirectory)
        base, ext = os.path.splitext(firstUnzippedFileName) # ext should be '.xml'
        singleRootFileName =base + '_SR' + ext
        pathToSingleRootFile = os.path.join(outputDirectory, singleRootFileName)
        create_single_root_file_from_PTO_file(pathToFirstUnzippedFile, pathToSingleRootFile)
        try:
            os.remove(pathToFirstUnzippedFile)
            try:
                os.remove(zippedXMLFile)
            except OSError as er:
                print(er)
                print('cant delete file ',zippedXMLFile)

        except OSError as er:
            print(er)
            print('cant delete file ',pathToFirstUnzippedFile)

if __name__ == "__main__":
    dataDirectory = ""
    patentDirectoryName = "patents"
    applicationDirectoryName = "applications"

    patentDirectory = os.path.join(dataDirectory,patentDirectoryName)
    applicationDirectory = os.path.join(dataDirectory,applicationDirectoryName)

    #take teh original xml file, split it into (thousands) of files
    # each of these files has just one application in its xml
    # inputFileName       = "/media/alderucci/Data/patent data/ipg181113.xml"
    # singleRootFileName  = "/media/alderucci/Data/patent data/ipg181113_SR.xml"
    # create_single_root_file_from_PTO_file(inputFileName, singleRootFileName)
    zipFileName = "PatentData1.zip"
    isPatent = True

    zipFileFullPath = os.path.join(dataDirectory, zipFileName)

    if isPatent:
        dirToUse = patentDirectory
    else:
        dirToUse = applicationDirectory
    unzipPTOFileAndCreateSingleRoot(zipFileFullPath, dirToUse)

    # directory = 'ipa181108'
    #
    # if not os.path.exists(directory):
    #     os.makedirs(directory)
    #
    # # create_single_root_file_from_PTO_file(inputFileName,singleRootFileName)
    # splitPTOXMLFileIntoManyFiles(inputFileName, directory)

    print('program complete')

