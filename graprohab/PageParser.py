# -*- coding: utf-8 -*-
"""
Created on Thu May 15 17:00:26 2014

@author: daniel
"""

from bs4 import BeautifulSoup
import re
import aux

"""
Default date format: YYYY-MM-DD

Instructions:
1) Download HTML code of page into the folder "pages_by_date" and name the file 
with the corresponding date in the default format. E.g. "2014-05-24" for May,24
2) Edit the date variable `meeting_date` and set the current date 
3) Run the script

"""


meeting_date = '2014-07-15'; #use default format YYYY-MM-DD

file_path = 'pages_by_date/'+meeting_date+'.html'



# -----------------------------------------------------------------------------
# FUNCTION THAT PARSES THE PAGE 
# -----------------------------------------------------------------------------

def parsePage(file_path, labels_dic):
    
    f = open(file_path, 'r')
    html = f.read();
    soup = BeautifulSoup(html, "html.parser")
    
    #get main info block - all main info is here
    main_info_block = soup.find(attrs={'id':'content'}).find(attrs={'class':'grid_24'})
    
    #get both tables
    content_tables = main_info_block.findAll("table")
    content_table = content_tables[0]
    label_table = content_tables[1]
    
    #parse labels
    p = re.compile(r'([0-9]+)')
    labels = p.split(label_table.get_text())
    labels.pop(0) #remove word 'Legenda'
    for i in range (0,len(labels)/2):
        labels_dic[labels[2*i]] = labels[2*i+1]
    print labels_dic
    
    #parse entries
    rows = content_table.findAll('tr')
    entry_info = {}
    list_of_entries = []
    for r in rows:
        #if entry info has ended, add entry to db
        if r.get_text().strip() == '':
            #check if is valid entry
            if isValidEntry(entry_info):
                #add to list
                #print '-------\n add to list: ' + str(entry_info)
                list_of_entries.append(entry_info)
            #reset entry
            entry_info={}
        #else, add info to entry
        else:
            cols = r.findAll('td')
            col_description = cols[0].get_text().strip()
            col_content = cols[1].get_text().strip()
            if u'N\xba de ordem' in col_description:
                p = re.compile(r':')
                split_description = p.split(col_description)
                col_description = split_description[0].strip()
                col_content = split_description[1].strip()
            entry_info[col_description] = col_content
            #print '-------\n info collected:' + col_description + ' -> ' + col_content
        
    return list_of_entries
    
# -----------------------------------------------------------------------------
# CHECKS IF AN ENTRY IS VALID (SOME ENTRIES ARE IRRELEVANT) 
# -----------------------------------------------------------------------------   

def isValidEntry(entry_info):
    if u'N\xba Protocolo' in entry_info.keys():
        return True
    return False

# -----------------------------------------------------------------------------
# GET ENTRY'S ORGANS 
# -----------------------------------------------------------------------------   

def getEntryOrgans(entry):
    organs = entry[u'Org\xe3os']
    organs_list = re.findall(r'\d+', organs)
    return organs_list
    
# -----------------------------------------------------------------------------
# PUT ALL DATA ON DATABASE
# ----------------------------------------------------------------------------- 
def putAllDataOnDatabase(list_of_entries, meeting_date, labels_dic):
    putEntriesInDatabase(list_of_entries, meeting_date)
    putEntryOrgansInDatabase(list_of_entries, meeting_date, labels_dic)
    return
    
# -----------------------------------------------------------------------------
# PUT ENTRIES IN DATABASE
# -----------------------------------------------------------------------------   
    
def putEntriesInDatabase(list_of_entries, meeting_date):
    for entry in list_of_entries:
        if not aux.entryExists(meeting_date, entry[u'N\xba de ordem']):
            aux.insertEntry(entry, meeting_date)
    return

# -----------------------------------------------------------------------------
# PUT ENTRY ORGANS IN DATABASE
# -----------------------------------------------------------------------------   
    
def putEntryOrgansInDatabase(list_of_entries, meeting_date, labels_dic):
    for entry in list_of_entries:
        organs_list = getEntryOrgans(entry)
        organs_list = [labels_dic[o] for o in organs_list]
        entry_id = aux.getEntryId(entry, meeting_date)
        aux.insertOrgans(entry_id, organs_list)
    return



labels_dic = {}
list_of_entries = parsePage(file_path, labels_dic)
putAllDataOnDatabase(list_of_entries, meeting_date, labels_dic)
    