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

base_file = 'all_properties_07-03-2014.txt'
base_url = 'http://www.centralnegocios.com.br'
file_folder = 'detailed_pages/'
sleep_time = 10

f = open(base_file, 'r')
html = f.read();

#pq = PyQuery(html)
#tag = pq('div.resultados_limite')
#print tag.text()


soup = BeautifulSoup(html, "html.parser")

list_of_postings = soup.find_all(attrs={'class':'resultados_imoveis'})

print 'total postings: ' + str(len(list_of_postings)) + '\n'

for posting in list_of_postings:
    
    #REFERENCE NUMBER + LAST UPDATE
    last_update_and_ref_num = posting.find(attrs={'class':'resultados_texto11'}).contents
    last_update = last_update_and_ref_num[0].split(': ')[-1]
    ref_num = last_update_and_ref_num[-1].split('Ref.: ')[-1]
    print 'last update: ' + last_update
    print 'reference: ' + ref_num + '\n'
    
    #TYPE + NEIGHBORHOOD + ADDRESS  
#    title_block = posting.find(attrs={'class':'resultados_imoveis_listatitulo'})    
#    title_block.div.extract() #remove ref_num part
#    propertyType_neighborhood = title_block.span.contents 
#    propertyType_neighborhood_split = propertyType_neighborhood[0].split(', ')
#    propertyType = propertyType_neighborhood_split[0]
#    neighborhood = propertyType_neighborhood_split[1]
#    print 'type: ' + propertyType
#    print 'neighborhood: ' + neighborhood + '\n'
    
    #GET LINK FOR DETAILED WEBPAGE
    detailed_link_path = posting.find(attrs={'class':'resultados_imoveis_botoes'})['href']
    detailed_link_path = detailed_link_path.replace("(","\(").replace(")","\)")
    current_link = base_url + detailed_link_path
    print 'link: ' + current_link + '\n'
    
    #CHECK IF LAST UPDATE WAS CRAWLED
    adjusted_date = last_update.replace("/","-")
    current_file_name = ref_num + '_' + adjusted_date + '.txt'
    print 'file name: ' + current_file_name
    if os.path.isfile(file_folder+current_file_name):
        continue
    
    #IF WASN'T CRAWLED, GET IT    
    crawling_command = 'curl '+ current_link + ' > ' + file_folder + current_file_name
    print crawling_command + '\n'
    os.system(crawling_command)
    print 'sleeping... \n'
    time.sleep(sleep_time)
    
    print '\n--------------------------------------------------- \n'
    
    #break

