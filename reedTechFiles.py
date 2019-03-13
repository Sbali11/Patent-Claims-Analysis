import requests
import lxml.html as lh
import pandas as pd



def processFile(fileName):
    if isPatentFileName(fileName):
        processingPatent = True
    else:
        processingPatent = False

    if needToDownloadFile(fileName, processingPatent):
        downloadFile(fileName)

# patent tables is a list of pandas data frames
def process_patent_tables(patent_tables):
    for table in tables:
        fileNames = table['File Name']
        print(type(fileNames))
        for fileName in fileNames:
            processFile(fileName)



def getAllPatentTablesFromReedTechSite():
    global tables
    patentsPageURL = "https://patents.reedtech.com/pgrbft.php"
    tables = pd.read_html(patentsPageURL, header=0)
    print(len(tables), ' tables found')
    # for table_index, table in enumerate(tables):
    #     print('table #', table_index)
    #     print(table.head())
    #     print()

    # first table is nothing, remaining tables all have patent data
    return tables[1:]

tables = getAllPatentTablesFromReedTechSite()

process_patent_tables(tables)



# #Create a handle, page, to handle the contents of the website
# page = requests.get(patentsPageURL)
#
# #Store the contents of the website under doc
# doc = lh.fromstring(page.content)
#
# #Parse data that are stored between <tr>..</tr> of HTML
# tr_elements = doc.xpath('//tr')
#
#
# #Create empty list
# col=[]
# i=0
# #For each row, store each first element (header) and an empty list
# for t in tr_elements[0]:
#     i+=1
#     name=t.text_content()
#     print('%d:"%s"'%(i,name))
#     col.append((name,[]))
#
# # Since out first row is the header, data is stored on the second row onwards
# for j in range(1, len(tr_elements)):
#     # T is our j'th row
#     T = tr_elements[j]
#
#     # If row is not of size 10, the //tr data is not from our table
#     if len(T) != 10:
#         break
#
#     # i is the index of our column
#     i = 0
#
#     # Iterate through each element of the row
#     for t in T.iterchildren():
#         data = t.text_content()
#         # Check if row is empty
#         if i > 0:
#             # Convert any numerical value to integers
#             try:
#                 data = int(data)
#             except:
#                 pass
#         # Append the data to the empty list of the i'th column
#         col[i][1].append(data)
#         # Increment i for the next column
#         i += 1
#
# Dict={title:column for (title,column) in col}
# df=pd.DataFrame(Dict)
#
# print(df.head())

print('program complete.')