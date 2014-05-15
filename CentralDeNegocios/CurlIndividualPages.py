# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 23:38:41 2014

@author: daniel
"""


#-------------------------------------------------------------------------
# To get the list of all properties, curl using the following page parameters (adjust it as necessary) : 
# http://www.centralnegocios.com.br/imoveis/venda/terrenos/10-maringa-pr/ordem-bairros.nome/limite-543
#
# currently used: http://www.centralnegocios.com.br/imoveis/venda/0-todas-pr/limite-2705
# curl http://www.centralnegocios.com.br/imoveis/venda/0-todas-pr/limite-2705 > all_properties_07-03-2014.txt
#-------------------------------------------------------------------------




from bs4 import BeautifulSoup
import os
import time
import aux
import re

crawl_date = '13-03-2014'
base_folder = 'all_properties_page/'
base_file = 'all_properties_'+crawl_date+'.txt'
base_url = 'http://www.centralnegocios.com.br'
file_folder = 'detailed_pages/'
sleep_time = 10

f = open(base_folder+base_file, 'r')
html = f.read();

#pq = PyQuery(html)
#tag = pq('div.resultados_limite')
#print tag.text()


soup = BeautifulSoup(html, "html.parser")

list_of_postings = soup.find_all(attrs={'class':'resultados_imoveis'})

#lists for keeping track of active postings
no_longer_observed_active = aux.getAllActiveRefNum()
new_active = []


print 'total postings: ' + str(len(list_of_postings)) + '\n'
total_new_postings = 0
for posting in list_of_postings:
    
    #REFERENCE NUMBER + LAST UPDATE
    last_update_and_ref_num = posting.find(attrs={'class':'resultados_texto11'}).contents
    last_update = last_update_and_ref_num[0].split(': ')[-1]
    ref_num = last_update_and_ref_num[-1].split('Ref.: ')[-1]
    print 'last update: ' + last_update
    print 'reference: ' + ref_num + '\n'
    
    
    #GET LINK FOR DETAILED WEBPAGE
    detailed_link_path = posting.find(attrs={'class':'resultados_imoveis_botoes'})['href']
    detailed_link_path = detailed_link_path.replace("(","\(").replace(")","\)")
    current_link = base_url + detailed_link_path
    print 'link: ' + current_link + '\n'
    
    #UPDATE ACTIVE LIST
    if ref_num in no_longer_observed_active:
        no_longer_observed_active.remove(ref_num)
    else:
        new_active.append(ref_num)
    
    #CHECK IF LAST UPDATE WAS CRAWLED
    adjusted_date = last_update.replace("/","-") #dd-mm-yyyy
    adjusted_date_reversed = "-".join(reversed(re.split("[-]",adjusted_date))) #yyyy-mm-dd
    
    #if entry exists on db
    if aux.entryExists(ref_num, adjusted_date_reversed):
        continue
    #if file exists (in case we have to rerun this script due to failures, in which case the db won't be updated)
    current_file_name = ref_num + '_' + adjusted_date + '.txt'
    if os.path.isfile(file_folder+current_file_name):
        continue
    
    #IF WASN'T CRAWLED, GET IT    
    crawling_command = 'curl '+ current_link + ' > ' + file_folder + current_file_name
    print crawling_command + '\n'
    os.system(crawling_command)
    total_new_postings += 1
    print 'sleeping... \n'
    time.sleep(sleep_time)    
    print '\n--------------------------------------------------- \n'


print "\nnew postings: "+ str(total_new_postings)
print "no longer active \n"
for ref in no_longer_observed_active:
    print "ref: " + ref
print "\nnew active \n"
for ref in new_active:
    print "ref: " + ref

#update db with sold properties
adjusted_crawl_date = "-".join(reversed(re.split("[-]",crawl_date))) #yyyy-mm-dd
aux.updateDbWithSoldProperties(no_longer_observed_active,adjusted_crawl_date)
#update db with active lists of properties (add new actives and remove no longer actives)
aux.updateDbWithActiveProperties(new_active,no_longer_observed_active)